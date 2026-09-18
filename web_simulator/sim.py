# -*- coding: utf-8 -*-
"""Padavan WebUI 后端模拟器 - Flask 入口"""

import os
import secrets

from flask import Flask, request, session, redirect, make_response, abort, send_from_directory

from .cgi_engine import render
from .nvram import get_nvram
from .dynstate import get_dyn
from .paths import get_webui_dir, get_dict_dir

STATIC_EXTS = {".css", ".png", ".gif", ".jpg", ".jpeg", ".ico", ".svg", ".map", ".bmp"}

app = Flask(__name__, static_folder=None)
app.secret_key = "padavan-sim-secret-key"

# ============================================================
#  辅助
# ============================================================

def render_asp(rel_path):
    full = os.path.join(get_webui_dir(), rel_path)
    if not os.path.isfile(full):
        abort(404)
    with open(full, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    html = render(src)
    resp = make_response(html)
    ext = os.path.splitext(rel_path)[1].lower()
    if ext == ".js":
        resp.headers["Content-Type"] = "application/javascript; charset=utf-8"
    elif ext in (".htm", ".html"):
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
    else:
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


def render_source(rel_path):
    """读源文件并渲染（返回字符串，不包 HTTP）"""
    full = os.path.join(get_webui_dir(), rel_path)
    if not os.path.isfile(full):
        return ""
    with open(full, "r", encoding="utf-8", errors="replace") as f:
        return render(f.read())

def is_template_file(full_path):
    """判断脚本是否包含 Padavan 模板标记。"""
    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()
    return "<%" in source or "<#" in source


def require_login(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("logged_in"):
            return redirect("/Login.asp")
        return fn(*a, **kw)
    return wrapper


# ============================================================
#  静态资源（按子目录分开注册，避免通配符冲突）
# ============================================================

@app.route("/bootstrap/<path:filename>")
def serve_bootstrap(filename):
    return send_from_directory(os.path.join(get_webui_dir(), "bootstrap"), filename)

@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(os.path.join(get_webui_dir(), "images"), filename)

@app.route("/dict/<path:filename>")
def serve_dict(filename):
    return send_from_directory(get_dict_dir(), filename)


# ============================================================
#  页面路由（在 catch_all 之前注册，优先级高）
# ============================================================

@app.route("/Login.asp", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        nv = get_nvram()
        expected_user = "admin"
        expected_pass = nv.get("", "http_passwd") or "admin"
        if u == expected_user and p == expected_pass:
            session.clear()
            session["logged_in"] = True
            session["sid"] = secrets.token_hex(16)
            return redirect("/")
        else:
            nv.set("", "login_fail_flag", "1")
    return render_asp("Login.asp")


@app.route("/Logout.asp", methods=["GET"])
@app.route("/logout", methods=["HEAD", "GET"])
def logout():
    if request.path.startswith("/logout"):
        session.clear()
        resp = make_response("")
        resp.headers["Content-Type"] = "text/plain"
        return resp
    session.clear()
    return render_asp("Logout.asp")


@app.route("/httpd_check.htm")
def httpd_check():
    return make_response("ASUSTeK")


@app.route("/start_apply.htm", methods=["GET", "POST"])
@require_login
def start_apply():
    return render_asp("start_apply.htm")


@app.route("/")
@app.route("/index.asp")
@require_login
def index():
    return render_asp("index.asp")


# ============================================================
#  通配 catch-all（处理所有其他路径）
# ============================================================

@app.route("/<path:path>")
def catch_all(path):
    # 1. 不需要登录的资源：静态文件（css/png/js未认证）
    full = os.path.join(get_webui_dir(), path)
    ext = os.path.splitext(path)[1].lower()

    # 纯静态透传（不走 CGI 渲染，也不要求登录）
    if os.path.isfile(full) and ext in STATIC_EXTS:
        return send_from_directory(get_webui_dir(), path)

    # 第三方或普通 JavaScript 不能经过模板渲染，否则可能被改写为无效脚本。
    if os.path.isfile(full) and ext == ".js" and not is_template_file(full):
        response = send_from_directory(get_webui_dir(), path)
        response.headers["Content-Type"] = "application/javascript; charset=utf-8"
        return response

    # 2. 以下需要登录
    if not session.get("logged_in"):
        return redirect("/Login.asp")

    # 3. update.cgi 专门处理
    if path == "update.cgi":
        return handle_update_cgi()

    # 4. CGI 实时数据接口（纯文本/JS 输出）
    if path == "status_wanlink.asp":
        resp = make_response(render_source("status_wanlink.asp"))
        resp.headers["Content-Type"] = "text/javascript; charset=utf-8"
        return resp
    if path == "status_internet.asp":
        resp = make_response(render_source("status_internet.asp"))
        resp.headers["Content-Type"] = "text/javascript; charset=utf-8"
        return resp
    if path == "lan_clients.asp":
        resp = make_response(render_source("lan_clients.asp"))
        resp.headers["Content-Type"] = "text/javascript; charset=utf-8"
        return resp
    if path == "system_status_data.asp":
        resp = make_response(render_source("system_status_data.asp"))
        resp.headers["Content-Type"] = "text/javascript; charset=utf-8"
        return resp

    # 5. .asp / .htm / .js 文件都走 CGI 引擎渲染
    if os.path.isfile(full):
        return render_asp(path)

    abort(404)


# ============================================================
#  update.cgi
# ============================================================

def handle_update_cgi():
    import json as _json
    out_type = request.args.get("output", "netdev")
    if out_type == "netdev":
        data = get_dyn().netdev()
        resp = make_response(data)
        resp.headers["Content-Type"] = "text/javascript; charset=utf-8"
        return resp
    if out_type == "wan_traffic":
        resp = make_response(_json.dumps(get_dyn().wan_status(), ensure_ascii=False))
        resp.headers["Content-Type"] = "application/json"
        return resp
    if out_type == "sysinfo":
        resp = make_response(_json.dumps(get_dyn().system_status(), ensure_ascii=False))
        resp.headers["Content-Type"] = "application/json"
        return resp
    abort(404)


# ============================================================
#  启动
# ============================================================

if __name__ == "__main__":
    host = os.environ.get("PADAVAN_SIM_HOST", "0.0.0.0")
    port = int(os.environ.get("PADAVAN_SIM_PORT", "8080"))
    debug = os.environ.get("PADAVAN_SIM_DEBUG", "1") != "0"
    print(f"\n{'='*60}")
    print(f" Padavan WebUI 后端模拟器启动中...")
    print(f" 本地 WebUI 目录: {get_webui_dir()}")
    print(f" 访问地址:   http://127.0.0.1:{port}/")
    print(f" 默认账号密码: admin / admin")
    print(f"{'='*60}\n")
    app.run(host=host, port=port, debug=debug)