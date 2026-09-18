# -*- coding: utf-8 -*-
"""Padavan 模拟器 - 硬件配置 & 默认 NVRAM 工厂值"""

# === 硬件参数 ===
BOARD_NAME = "ZVMODELVZ"
BOARD_PRODUCT_ID = "ASUS_RT-N56U"
FIRMWARE_VERSION = "3.4.3.9-099_23-gf2e666d-dirty"
FIRMWARE_BUILD = "20260915"
FIRMWARE_PROFILE = "asus"
BOARD_HAS_2G = True
BOARD_HAS_5G = True
BOARD_HAS_ATA = False
BOARD_HAS_USB = True
FIRMWARE_INCLUDE_IPV6 = True
FIRMWARE_INCLUDE_LANG_CN = True
FIRMWARE_INCLUDE_LANG_EN = True

# === MAC 地址 ===
MAC_WAN = "00:11:22:33:44:55"
MAC_LAN = "00:11:22:33:44:56"
MAC_2G  = "00:11:22:33:44:57"
MAC_5G  = "00:11:22:33:44:58"

# === 固件功能开关（影响模板中 firmware_caps_hook 输出）===
FEATURES = [
    "USB_SUPPORT",
    "STORAGE",
    "FIRMWARE_INCLUDE_SHADOWSOCKS",
    "FIRMWARE_INCLUDE_DNSFORWARDER",
    "FIRMWARE_INCLUDE_MENTOHUST",
    "FIRMWARE_INCLUDE_SCUTCLIENT",
    "FIRMWARE_INCLUDE_OPENVPN_WEBUI",
    "FIRMWARE_INCLUDE_VPNC_WEBUI",
]

# === 默认 NVRAM 值 ===
DEFAULT_NVRAM = {
    "General": {
        "help_enable": "1",
        "preferred_lang": "EN",
    },
    "LANHostConfig": {
        "lan_ipaddr": "192.168.1.1",
        "lan_netmask": "255.255.255.0",
        "lan_proto_x": "static",
        "dhcp_enable": "1",
        "dhcp_start": "192.168.1.100",
        "dhcp_end": "192.168.1.200",
        "time_zone": "CST-8",
        "ntp_period": "24",
        "ntp_server0": "pool.ntp.org",
        "ntp_server1": "time.google.com",
        "computer_name": "Padavan-Router",
    },
    "WAN": {
        "wan_proto": "dhcp",
        "wan_route_x": "IP_Routed",
        "link_internet": "1",
        "sw_mode": "0",
        "fw_enable_x": "1",
    },
    "Wireless": {
        "wl_enable": "1",
        "wl_ssid": "Padavan-5G",
        "wl_auth_mode": "psk",
        "wl_wpa_mode": "2",
        "wl_wpa_psk": "87654321",
        "wl_chanspec": "36",
        "wl_bandwidth": "20/40",
        "wl_mcast_rate": "1200",
    },
    "Wireless2": {
        "rt_enable": "1",
        "rt_ssid": "Padavan-2.4G",
        "rt_auth_mode": "psk",
        "rt_wpa_mode": "2",
        "rt_wpa_psk": "12345678",
        "rt_chanspec": "6",
        "rt_bandwidth": "20",
        "rt_mcast_rate": "650",
    },
    "FirewallConfig": {
        "macfilter_enable_x": "0",
        "MFList": "",
    },
    "LANHostConfig;General;Storage": {
        # start_apply.htm 默认的 sid_list 合并组
    },
}

# 把默认 NVRAM 展平为 key 式访问 (section.key = value)
def flatten_nvram():
    result = {}
    for section, items in DEFAULT_NVRAM.items():
        for k, v in items.items():
            result[f"{section}.{k}"] = v
    return result