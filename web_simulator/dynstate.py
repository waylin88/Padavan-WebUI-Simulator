# -*- coding: utf-8 -*-
"""Padavan 动态状态模拟 - WAN 连接、客户端、流量、USB 设备、系统"""

import time
import random
import threading
from typing import Any, Dict, List

class DynState:
    """模拟实时变化的硬件状态"""

    def __init__(self):
        self._lock = threading.RLock()
        self.boot_time = time.time() - 3600 * 2  # 模拟已开机 2 小时
        self.wan_connect_time = time.time() - 3000

        self._cpu_tick = 0
        self._cpu_busy = 0

        # WAN 流量累计字节
        self.wan_bytes_rx = 0x00A1B2C3
        self.wan_bytes_tx = 0x00C3B2A1

        # 网络设备 RX/TX 累计 (接口名 -> {rx, tx, id})
        self._netdev_counters = {
            "LAN": {"id": 0, "rx": 0x01000000, "tx": 0x00800000},
            "WAN": {"id": 0, "rx": 0x00800000, "tx": 0x00400000},
            "2G":  {"id": 0, "rx": 0x00200000, "tx": 0x00100000},
            "5G":  {"id": 0, "rx": 0x00300000, "tx": 0x00180000},
        }

        # 客户端列表: [name, ip, mac, rssi, speed, type, wl_enc, block]
        self.clients: List[list] = [
            ["Laptop-Dell",   "192.168.1.101", "AA:BB:CC:DD:EE:01", -45, 867000, 6, 10, "u"],
            ["iPhone-15",     "192.168.1.102", "AA:BB:CC:DD:EE:02", -58, 300000, 5, 10, "u"],
            ["Xiaomi-MI-14",  "192.168.1.103", "AA:BB:CC:DD:EE:03", -62, 300000, 5, 10, "u"],
            ["TV-Samsung",    "192.168.1.104", "AA:BB:CC:DD:EE:04", -70, 150000, 6, 10, "u"],
            ["MacBook-Pro",   "192.168.1.105", "AA:BB:CC:DD:EE:05",    0,      10, 0, 10, "u"],
            ["PC-Desktop",    "192.168.1.106", "AA:BB:CC:DD:EE:06",    0,      10, 0, 10, "u"],
        ]

        # WAN 扫描结果 (模拟 wl_scan)
        self.wl_scan_2g = [
            ["Padavan-2.4G", "AA:BB:CC:DD:EE:00", -35, 6, "WPA2PSK/AES"],
            ["TP-LINK_4F2A", "AA:BB:CC:DD:EE:11", -65, 6, "WPA2PSK/AES"],
            ["CMCC-FREE",    "AA:BB:CC:DD:EE:22", -72, 1, "OPEN"],
        ]
        self.wl_scan_5g = [
            ["Padavan-5G",   "AA:BB:CC:DD:EE:FF", -30, 36, "WPA2PSK/AES"],
            ["ASUS-5G-Guest", "AA:BB:CC:DD:EE:EE", -55, 44, "WPA2PSK/AES"],
        ]

        # USB / 磁盘
        self.usb_ports = [2, 0]   # [USB1=storage, USB2=none]
        self.disks = [
            {"model": "SanDisk Ultra 64GB", "size": 64 * 1024 * 1024 * 1024, "used": 30 * 1024 * 1024 * 1024, "interface": "1"},
        ]
        self.disk_pool = [
            ["pool1", "1"],
        ]

        # 日志 (环形缓冲)
        self.log_lines: List[str] = []
        for i in range(50):
            self.log_lines.append(f"{int(time.time()) - i * 5} kernel: [{i:4d}] init done ({i})")

    # === WAN ===
    def wan_status(self):
        """返回 (scode, wtype, uptime, dltime, ip4, gw4, dns, mac, bytes_rx, bytes_tx)"""
        scode = 0       # 0=已连接
        wtype = "Automatic IP"
        uptime = int(time.time() - self.wan_connect_time)
        dltime = 86400 - (uptime % 86400)
        ip4 = "100.87.234.156"
        gw4 = "100.87.234.1"
        dns = "223.5.5.5, 114.114.114.114"
        mac = "00:11:22:33:44:55"
        self.wan_bytes_rx += random.randint(500, 5000)
        self.wan_bytes_tx += random.randint(200, 2000)
        return (scode, wtype, uptime, dltime, ip4, gw4, dns, mac,
                self.wan_bytes_rx, self.wan_bytes_tx)

    def wan_etherlink(self):
        return "1 Gbps, Full Duplex"

    def wan_apcli_link(self):
        return ""

    # === 系统 ===
    def system_status(self) -> dict:
        """json_system_status() 返回的 JSON 结构 —— 必须与 setSystemInfo() 期望完全一致"""
        delta = random.randint(50, 200)
        load = random.uniform(0.02, 0.40)
        busy_delta = int(delta * load)
        self._cpu_tick += delta
        self._cpu_busy += busy_delta
        idle_delta = delta - busy_delta

        user_d    = int(busy_delta * 0.40)
        system_d  = int(busy_delta * 0.35)
        nice_d    = int(busy_delta * 0.05)
        iowait_d  = int(busy_delta * 0.08)
        irq_d     = int(busy_delta * 0.05)
        sirq_d    = int(busy_delta * 0.07)

        if not hasattr(self, '_cpu_user'):   self._cpu_user    = 0
        if not hasattr(self, '_cpu_system'): self._cpu_system  = 0
        if not hasattr(self, '_cpu_nice'):   self._cpu_nice    = 0
        if not hasattr(self, '_cpu_iowait'): self._cpu_iowait  = 0
        if not hasattr(self, '_cpu_irq'):    self._cpu_irq     = 0
        if not hasattr(self, '_cpu_sirq'):   self._cpu_sirq    = 0
        if not hasattr(self, '_cpu_idle'):   self._cpu_idle    = 0

        self._cpu_user    += user_d
        self._cpu_system  += system_d
        self._cpu_nice    += nice_d
        self._cpu_iowait  += iowait_d
        self._cpu_irq     += irq_d
        self._cpu_sirq    += sirq_d
        self._cpu_idle    += idle_delta

        mem_total = 256 * 1024
        mem_free  = int(mem_total * random.uniform(0.35, 0.55))
        mem_used  = mem_total - mem_free
        mem_cached = int(mem_free * 0.3)
        mem_buffers = int(mem_free * 0.15)
        swap_total = 64 * 1024
        swap_used  = int(swap_total * random.uniform(0.0, 0.05))

        uptime_sec = int(time.time() - self.boot_time)
        days = uptime_sec // 86400
        hours = (uptime_sec % 86400) // 3600
        minutes = (uptime_sec % 3600) // 60

        la1 = round(load * random.uniform(0.8, 1.2), 2)
        la5 = round(la1 * random.uniform(0.6, 0.9), 2)
        la15 = round(la5 * random.uniform(0.5, 0.8), 2)

        return {
            "cpu": {
                "total":   self._cpu_tick,
                "busy":    self._cpu_busy,
                "user":    self._cpu_user,
                "nice":    self._cpu_nice,
                "system":  self._cpu_system,
                "idle":    self._cpu_idle,
                "iowait":  self._cpu_iowait,
                "irq":     self._cpu_irq,
                "sirq":    self._cpu_sirq,
            },
            "ram": {
                "total":    mem_total,
                "free":     mem_free,
                "used":     mem_used,
                "cached":   mem_cached,
                "buffers":  mem_buffers,
            },
            "swap": {
                "total": swap_total,
                "used":  swap_used,
            },
            "lavg": f"{la1:.2f} {la5:.2f} {la15:.2f}",
            "uptime": {
                "days":    days,
                "hours":   hours,
                "minutes": minutes,
            },
            "wifi2": {
                "state": 1,
                "guest": 0,
            },
            "wifi5": {
                "state": 1,
                "guest": 0,
            },
            "logmt": int(time.time()),
            "version": {
                "product_id": "ZVMODELVZ",
                "fw_version": "3.4.3.9-Padavan",
                "build_date": "20260915",
                "kernel": "3.4.113",
            },
        }

    def uptime_str(self) -> str:
        """Padavan uptime() 格式: 'Wed Sep 15 10:33:31 2026 - 1 days 02:15:27'"""
        from datetime import datetime
        now = datetime.now()
        up = int(time.time() - self.boot_time)
        days = up // 86400
        hh = (up // 3600) % 24
        mm = (up // 60) % 60
        ss = up % 60
        return f"{now.strftime('%a %b %d %H:%M:%S %Y')} - {days} days {hh:02d}:{mm:02d}:{ss:02d}"

    def board_boot_time(self) -> int:
        """重启等待秒数"""
        return 30

    # === 客户端 ===
    def get_static_client(self) -> str:
        """get_static_client() - 生成客户端 JS 数组字符串"""
        out = []
        for c in self.clients:
            name, ip, mac, rssi, speed, devtype, wl_enc, block = c
            wl = 1 if rssi != 0 else 0
            entry = f'["{name}","{ip}","{mac}",{rssi},{speed},{devtype},{wl},"{block}"]'
            out.append(entry)
        return ",".join(out)

    # === 网络设备流量 ===
    def netdev(self) -> str:
        """netdev() - /update.cgi?output=netdev 调用"""
        out = []
        for ifname, c in self._netdev_counters.items():
            c["rx"] += random.randint(1000, 20000)
            c["tx"] += random.randint(500, 10000)
            out.append(
                f"'{ifname}': {{ id:{c['id']}, rx:{c['rx']}, tx:{c['tx']} }}"
            )
        return "var netdevs = { " + ", ".join(out) + " };"

    # === USB / 磁盘 ===
    def usb_ports_info(self):
        return self.usb_ports

    def get_device_type_usb(self, port):
        idx = port - 1
        if idx < len(self.usb_ports):
            t = self.usb_ports[idx]
            return ["", "storage", "printer", "modem_tty", "hub"][t] if t < 5 else ""
        return ""

    def foreign_disks(self):
        return [d["model"] for d in self.disks]

    def foreign_disk_total_size(self):
        return [d["size"] for d in self.disks]

    def foreign_disk_interface_names(self):
        return [d["interface"] for d in self.disks]

    def foreign_disk_model_info(self):
        return [d["model"] for d in self.disks]

    def blank_disks(self):
        return []

    def blank_disk_total_size(self):
        return []

    def getDiskMountedNum(self, order):
        return 1

    # === 日志 ===
    def log_content(self) -> str:
        return "\n".join(self.log_lines)

    def console_response(self) -> str:
        """Console.asp 模拟"""
        return ""

_dyn = DynState()
def get_dyn() -> DynState:
    return _dyn