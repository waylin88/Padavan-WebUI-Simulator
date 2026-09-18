# -*- coding: utf-8 -*-
"""从 www/dict/*.dict 加载语言字典"""

import os
import configparser
from .paths import get_dict_dir

# 合并 EN.header + EN.footer 作为默认英文 EN.dict
def _load_single_dict(path):
    """Padavan dict 文件是 'key=value' 格式，# 开头注释"""
    d = {}
    if not os.path.isfile(path):
        return d
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                d[k.strip()] = v
    return d

def load_all():
    """加载所有语言字典，返回 {lang_code: {...dict...}}"""
    dicts = {}
    d = get_dict_dir()
    en_h = _load_single_dict(os.path.join(d, "EN.header"))
    en_f = _load_single_dict(os.path.join(d, "EN.footer"))
    dicts["EN"] = {**en_h, **en_f}

    for fname in os.listdir(d):
        if fname.endswith(".dict") and fname != "EN.header":
            code = fname.replace(".dict", "")
            dicts[code] = _load_single_dict(os.path.join(d, fname))

    return dicts

_DICTS = {}
_DICTS_DIR = None
def get_dict(lang="EN"):
    global _DICTS, _DICTS_DIR
    cur = get_dict_dir()
    if _DICTS_DIR != cur:
        _DICTS = load_all()
        _DICTS_DIR = cur
    if lang not in _DICTS:
        lang = "EN"
    return _DICTS[lang]

def translate(key, lang="EN"):
    d = get_dict(lang)
    return d.get(key, d.get(key, f"<{key}>"))