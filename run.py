# -*- coding: utf-8 -*-
"""独立仓库启动入口 - python run.py --www <path>"""
import os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from web_simulator.__main__ import main

if __name__ == "__main__":
    main()
