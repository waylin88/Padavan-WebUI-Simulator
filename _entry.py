# -*- coding: utf-8 -*-
"""PyInstaller 打包专用入口 - 不使用相对 import"""

import sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from web_simulator.__main__ import main

if __name__ == "__main__":
    main()