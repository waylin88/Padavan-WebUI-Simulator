# -*- coding: utf-8 -*-
"""NVRAM 模拟器 - 完全复刻 Padavan nvram_get/match/set/dump 语义"""

import threading
from .config import DEFAULT_NVRAM, flatten_nvram

class NVRAM:
    """Padavan NVRAM 内存模拟器"""

    def __init__(self):
        self._lock = threading.RLock()
        self._data = {}   # {"section": {"key": "value"}}
        self._flat = {}   # {"section.key": "value"}
        self._init_defaults()

    def _init_defaults(self):
        with self._lock:
            for section, items in DEFAULT_NVRAM.items():
                self._data.setdefault(section, {})
                for k, v in items.items():
                    self._data[section][k] = str(v)
                    self._flat[f"{section}.{k}"] = str(v)

    # === 读 ===
    def get(self, section, key, default=""):
        """nvram_get_x(section, key)
        - 有 section: 只查该 section
        - 空 section: 扫描所有 section（Padavan 原生 NVRAM 是扁平单空间）
        """
        with self._lock:
            if section:
                if section in self._data:
                    return self._data[section].get(key, default)
                return default
            # 空 section -> 扁平搜索所有分组
            for sec_name, items in self._data.items():
                if key in items:
                    return items[key]
            return default

    def match(self, section, key, expected, output=""):
        """nvram_match_x - 如果值匹配则返回 output（通常是 'selected' / 'checked' 等）"""
        val = self.get(section, key)
        return output if val == expected else ""

    def dump(self, key, default=""):
        """nvram_dump(key, default) - 用于大块文本 (ovpnsvr.server.conf 等)
        搜索所有 section 里的 key，也支持无 section 的 flat key"""
        with self._lock:
            if "." in key:
                val = self._flat.get(key)
                if val:
                    return val
            else:
                for sec_name, items in self._data.items():
                    if key in items:
                        val = items[key]
                        if val:
                            return val
            return default

    # === 写 ===
    def set(self, section, key, value):
        with self._lock:
            section = section or "General"
            self._data.setdefault(section, {})
            self._data[section][key] = str(value)
            self._flat[f"{section}.{key}"] = str(value)

    def set_flat(self, dotted_key, value):
        with self._lock:
            self._flat[dotted_key] = str(value)
            if "." in dotted_key:
                section, key = dotted_key.split(".", 1)
                self._data.setdefault(section, {})
                self._data[section][key] = str(value)

    def commit(self):
        """asus_nvram_commit() - 实际固件中写 flash，这里只是个标记"""
        pass

    def commit_for_flash(self):
        return 0

    # === 辅助 ===
    def get_list(self, section, key, extra=None):
        """get_nvram_list(section, key) - 解析形如 'mac1@name1;mac2@name2' 的列表"""
        val = self.get(section, key) or ""
        result = []
        if val.strip():
            for entry in val.split(";"):
                if entry.strip():
                    # 尝试按 @ 和 _ 拆分，Padavan 用 @ 作为分隔
                    parts = entry.split("@")
                    result.append(parts)
        return result

    def keys(self, section=None):
        if section:
            return list(self._data.get(section, {}).keys())
        return list(self._flat.keys())

    def all(self):
        return dict(self._flat)

# 单例
_nvram_instance = None
_nvram_lock = threading.Lock()

def get_nvram() -> NVRAM:
    global _nvram_instance
    if _nvram_instance is None:
        with _nvram_lock:
            if _nvram_instance is None:
                _nvram_instance = NVRAM()
    return _nvram_instance