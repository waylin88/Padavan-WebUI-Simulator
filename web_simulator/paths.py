# -*- coding: utf-8 -*-
"""统一管理 WWW 相关路径，支持运行时覆盖。

解析优先级（从高到低）:
  1. set_www_dir() 显式设置的值
  2. PADAVAN_SIM_WWW 环境变量
  3. 可执行文件（PyInstaller 打包）所在目录的 ./www
  4. 本包所在目录的 ../www  (开发模式)
"""

import os
import sys

_OVERRIDE = None


def set_www_dir(path):
    global _OVERRIDE
    _OVERRIDE = os.path.abspath(path)


def get_www_dir():
    if _OVERRIDE:
        return _OVERRIDE
    env = os.environ.get("PADAVAN_SIM_WWW")
    if env:
        return os.path.abspath(env)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        return os.path.join(exe_dir, "www")
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(this_dir, "..", "www"))


def get_webui_dir():
    return os.path.join(get_www_dir(), "n56u_ribbon_fixed")


def get_dict_dir():
    return os.path.join(get_www_dir(), "dict")