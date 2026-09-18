# -*- coding: utf-8 -*-
"""CLI 入口 - python -m web_simulator 或 PyInstaller 打包成 exe

参数:
  --www PATH     指定 WWW 根目录 (需包含 n56u_ribbon_fixed/ 和 dict/)
  --host HOST    监听地址 (默认 0.0.0.0)
  --port PORT    监听端口 (默认 8080)
  --debug        开启 Flask debug 模式
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="padavan-sim",
        description="Padavan WebUI 模拟器 - 独立可执行版本",
    )
    parser.add_argument("--www", metavar="PATH",
                        help="WWW 根目录 (需包含 n56u_ribbon_fixed/ 和 dict/)")
    parser.add_argument("--host", default=os.environ.get("PADAVAN_SIM_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("PADAVAN_SIM_PORT", "8080")))
    parser.add_argument("--debug", action="store_true",
                        default=os.environ.get("PADAVAN_SIM_DEBUG", "0") == "1")
    args = parser.parse_args()

    if args.www:
        from .paths import set_www_dir
        set_www_dir(args.www)

    from .paths import get_www_dir, get_webui_dir, get_dict_dir

    www = get_www_dir()
    webui = get_webui_dir()
    dicts = get_dict_dir()

    def check_exists(path, label):
        if not os.path.isdir(path):
            print(f"[错误] {label} 不存在: {path}", file=sys.stderr)
            return False
        return True

    ok = True
    ok &= check_exists(www, "WWW 根目录")
    ok &= check_exists(webui, "WebUI 子目录 (n56u_ribbon_fixed)")
    ok &= check_exists(dicts, "字典子目录 (dict)")
    if not ok:
        print("\n  目录结构应为:", file=sys.stderr)
        print(f"  {www}/", file=sys.stderr)
        print(f"  ├─ n56u_ribbon_fixed/", file=sys.stderr)
        print(f"  └─ dict/", file=sys.stderr)
        sys.exit(1)

    from .sim import app

    print()
    print("  >>> Padavan WebUI 模拟器 <<<")
    print(f"    WWW 目录:   {www}")
    print(f"    访问地址:   http://127.0.0.1:{args.port}/")
    print(f"    默认账号:   admin / admin")
    print(f"    按 Ctrl+C 停止\n")
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()