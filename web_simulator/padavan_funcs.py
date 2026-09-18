# -*- coding: utf-8 -*-
"""Padavan CGI 后端函数全集 - 被 <% func(args) %> 语法调用"""

import json
import time
import random
from datetime import datetime
from .nvram import get_nvram
from .dynstate import get_dyn
from .language import translate
from .config import (
    BOARD_NAME, FIRMWARE_VERSION, FIRMWARE_BUILD, FIRMWARE_PROFILE,
    FIRMWARE_INCLUDE_LANG_CN, FIRMWARE_INCLUDE_LANG_EN, FIRMWARE_INCLUDE_IPV6, FEATURES,
    BOARD_HAS_2G, BOARD_HAS_5G, BOARD_HAS_USB, BOARD_HAS_ATA,
    MAC_WAN, MAC_LAN, MAC_2G, MAC_5G,
)

def _req():
    """延迟引入，避免循环依赖 - Flask request 在调用时才拿"""
    from flask import request as _r
    return _r

def _nv():  return get_nvram()
def _dy():  return get_dyn()

# ============================================================
#  基本 NVRAM 函数（最常用）
# ============================================================

def nvram_get_x(section, key):
    """<% nvram_get_x("section", "key") %>"""
    return _nv().get(section, key)

def nvram_match_x(section, key, expected, output=""):
    """<% nvram_match_x("section", "key", "val", "selected") %>"""
    return _nv().match(section, key, expected, output)

def nvram_dump(key, default=""):
    """<% nvram_dump("key", "") %> - 用于大块文本（JS 赋值或 textarea）"""
    val = _nv().dump(key, default)
    if not val and not default:
        return "[]"
    return val

def nvram_char_to_ascii(section, key):
    """<% nvram_char_to_ascii("", "key"); %> - 类似 nvram_get_x，Padavan 内部做了 ASCII 字符转换"""
    return _nv().get(section, key)

def nvram_double_match_x(section, key, expected1, expected2, output=""):
    """<% nvram_double_match_x("s", "k", "v1", "v2", "selected"); %>"""
    val = _nv().get(section, key)
    return output if val == expected1 or val == expected2 else ""

def nvram_get_ddns(section, key):
    return _nv().get(section, key)

def nvram_get_table_x(section, key, *extra):
    """<% nvram_get_table_x("section", "key"); %> - Padavan 内部表查询"""
    return ""

# ============================================================
#  参数获取
# ============================================================

def get_parameter(name):
    """<% get_parameter("flag") %> - 从 URL query 或 POST 取参数"""
    r = _req()
    return r.args.get(name, r.form.get(name, ""))

def get_flash_time():
    """<% get_flash_time() %> - 渲染 JS: var restart_time = N;"""
    t = _nv().get("", "flash_time", "0")
    return f"var restart_time = {t};"

# ============================================================
#  WAN / 网络状态
# ============================================================

def wanlink():
    """<% wanlink(); %> - 渲染闭包变量 + 所有 JS getter 函数"""
    s = _dy().wan_status()
    scode, wtype, uptime, dltime, ip4, gw4, dns, mac, rxb, txb = s
    state_line = (
        f"var __wan_state={{scode:{scode},wtype:'{wtype}',uptime:{uptime},"
        f"dltime:{dltime},ip4:'{ip4}',gw4:'{gw4}',dns:'{dns}',mac:'{mac}',"
        f"rxb:{rxb},txb:{txb}}};"
    )
    funcs = (
        "function wanlink_status(){return __wan_state.scode;}"
        "function wanlink_type(){return __wan_state.wtype;}"
        "function wanlink_uptime(){return __wan_state.uptime;}"
        "function wanlink_dltime(){return __wan_state.dltime;}"
        "function wanlink_ip4_wan(){return __wan_state.ip4;}"
        "function wanlink_gw4_wan(){return __wan_state.gw4;}"
        "function wanlink_dns(){return __wan_state.dns;}"
        "function wanlink_mac(){return __wan_state.mac;}"
        "function wanlink_bytes_rx(){return __wan_state.rxb;}"
        "function wanlink_bytes_tx(){return __wan_state.txb;}"
        "function wanlink_etherlink(){return 1;}"
        "function wanlink_apclilink(){return 0;}"
        "function wanlink_ip4_man(){return '';}"
        "function wanlink_gw4_man(){return '';}"
        "function wanlink_ip6_wan(){return '';}"
        "function wanlink_ip6_lan(){return '';}"
    )
    return state_line + funcs

def detect_internet():
    """<% detect_internet(); %> - 无输出，实际固件中后台检测"""
    return ""

# ============================================================
#  系统状态
# ============================================================

def json_system_status():
    """<% json_system_status(); %> - 输出 JSON 对象（不含 var 声明）"""
    return json.dumps(_dy().system_status(), ensure_ascii=False)

def uptime():
    """<% uptime(); %> - 输出 uptime 字符串"""
    return _dy().uptime_str()

def board_boot_time():
    """<% board_boot_time(); %> - 整数秒"""
    return _dy().board_boot_time()

def netdev():
    """<% netdev(); %> - 输出 JS var netdevs = {...};"""
    return _dy().netdev()

# ============================================================
#  客户端
# ============================================================

def get_static_ccount():
    return len(_dy().clients)

def get_static_client():
    """<% get_static_client(); %>"""
    return _dy().get_static_client()

def get_nvram_list(section, key, *extra):
    """<% get_nvram_list("section", "key") %> - 格式化成 JS 数组字符串"""
    lst = _nv().get_list(section, key)
    out = []
    for entry in lst:
        # 每个 entry 可能是 1-N 个字段
        fields = [f'"{e}"' if e is not None else "null" for e in entry]
        out.append("[" + ",".join(fields) + "]")
    return ",".join(out)

def wl_auth_list():
    """<% wl_auth_list(); %> - 客户端认证信息"""
    clients = _dy().clients
    items = []
    for c in clients:
        items.append(f'"{c[2]}":[{{}}]')
    return ",".join(items)

# ============================================================
#  USB / 磁盘
# ============================================================

def disk_pool_mapping_info():
    out = _dy().disk_pool
    arr = ",".join(f'["{a}","{b}"]' for a, b in out)
    return f"var disk_pool_mapping_info = [{arr}];"

def available_disk_names_and_sizes():
    dyn = _dy()
    names = dyn.foreign_disks() + dyn.blank_disks()
    sizes = dyn.foreign_disk_total_size() + dyn.blank_disk_total_size()
    arr = ",".join(f'["{n}",{s}]' for n, s in zip(names, sizes))
    return f"var available_disks = [{arr}];"

def get_usb_ports_info():
    ports = _dy().usb_ports_info()
    arr = ",".join(str(p) for p in ports)
    return f"var usb_dev_types = [{arr}];"

def get_ext_ports_info():
    return "var ext_ports_info = [];"

def foreign_disks():
    arr = ",".join(f'"{d}"' for d in _dy().foreign_disks())
    return f"[{arr}]"

def foreign_disk_interface_names():
    arr = ",".join(f'"{n}"' for n in _dy().foreign_disk_interface_names())
    return f"[{arr}]"

def foreign_disk_model_info():
    arr = ",".join(f'"{n}"' for n in _dy().foreign_disk_model_info())
    return f"[{arr}]"

def foreign_disk_total_size():
    arr = ",".join(str(s) for s in _dy().foreign_disk_total_size())
    return f"[{arr}]"

def blank_disks(): return "[]"
def blank_disk_total_size(): return "[]"
def blank_disk_interface_names(): return "[]"

# ============================================================
#  WiFi 扫描
# ============================================================

def wl_scan_2g():
    arr = []
    for e in _dy().wl_scan_2g:
        arr.append(f'{{ssid:"{e[0]}",bssid:"{e[1]}",rssi:{e[2]},ch:{e[3]},crypto:"{e[4]}"}}')
    return "[" + ",".join(arr) + "]"

def wl_scan_5g():
    arr = []
    for e in _dy().wl_scan_5g:
        arr.append(f'{{ssid:"{e[0]}",bssid:"{e[1]}",rssi:{e[2]},ch:{e[3]},crypto:"{e[4]}"}}')
    return "[" + ",".join(arr) + "]"

# ============================================================
#  语言
# ============================================================

def shown_language_option():
    """<% shown_language_option(); %> - 渲染 language 下拉框"""
    opts = []
    lang_code = _nv().get("", "preferred_lang", "EN")
    langs = [("EN", "English"), ("CN", "简体中文"), ("BR", "Brazil"),
             ("CZ", "Česky"), ("DA", "Dansk"), ("DE", "Deutsch"),
             ("ES", "Español"), ("FI", "Finsk"), ("FR", "Français"),
             ("NO", "Norsk"), ("PL", "Polski"), ("RU", "Pусский"),
             ("SV", "Svensk"), ("UK", "Українська")]
    for code, name in langs:
        sel = ' selected="selected"' if code == lang_code else ""
        opts.append(f'<option value="{code}"{sel}>{name}</option>')
    return "\n".join(opts)

# ============================================================
#  登录/会话钩子
# ============================================================

def login_state_hook():
    """<% login_state_hook(); %> - 在模板开头检查登录状态，未登录则重定向"""
    from flask import session, redirect, _app_ctx_stack
    # 实际运行时检查；如果是渲染阶段且 session 无认证，输出 JS 跳转
    if not session.get("logged_in"):
        return (
            '<script>top.location.href="/Login.asp";</script>'
        )
    return ""

def login_safe():
    """<% login_safe() %> - 密码安全模式（已修改过密码则隐藏密码字段）"""
    # 模拟器中始终返回 0，让密码字段显示
    return 0

# ============================================================
#  固件能力 / 硬件功能
# ============================================================

def firmware_caps_hook():
    """<% firmware_caps_hook(); %> - 在 state.js 中输出一堆 support_xxx() JS 函数"""
    lines = []
    lines.append("function support_2g_radio(){return %d;}" % int(BOARD_HAS_2G))
    lines.append("function support_5g_radio(){return %d;}" % int(BOARD_HAS_5G))
    lines.append("function get_ap_mode(){return (wan_route_x == 'IP_Bridged' || sw_mode == '3') ? true : false;}")
    lines.append("function board_boot_time(){return %d;}" % _dy().board_boot_time())
    lines.append("function support_ipv6(){return %d;}" % int(FIRMWARE_INCLUDE_IPV6))
    lines.append("function support_num_ephy(){return 4;}")
    lines.append("function support_storage(){return %d;}" % int(BOARD_HAS_USB or BOARD_HAS_ATA))
    lines.append("function support_usb(){return %d;}" % int(BOARD_HAS_USB))
    lines.append("function get_ata_support(){return %d;}" % int(BOARD_HAS_ATA))
    lines.append("function get_mmc_support(){return 0;}")
    lines.append("function found_app_scutclient(){return false;}")
    lines.append("function found_app_dnsforwarder(){return false;}")
    lines.append("function found_app_shadowsocks(){return false;}")
    lines.append("function found_app_mentohust(){return false;}")
    lines.append("function found_app_smbd(){return false;}")
    lines.append("function found_app_ftpd(){return false;}")
    lines.append("function get_usb_ports_num(){return %d;}" % len(_dy().usb_ports_info()))
    lines.append("function get_device_type_usb(p){ return ''; }")
    lines.append("function getDiskMountedNum(o){return 1;}")
    lines.append("function foreign_disks(){return [];}")
    lines.append("function blank_disks(){return [];}")
    lines.append("function foreign_disk_interface_names(){return [];}")
    lines.append("function foreign_disk_total_size(){return [];}")
    lines.append("function foreign_disk_model_info(){return [];}")
    lines.append("function blank_disk_interface_names(){return [];}")
    lines.append("function blank_disk_total_size(){return [];}")
    lines.append("function modem_devnum(){return [];}")
    lines.append("function printer_ports(){return [];}")
    lines.append("function modem_ports(){return [];}")
    lines.append("function ccount(){return %d;}" % get_static_ccount())
    lines.append("function get_static_ccount(){return %d;}" % get_static_ccount())
    lines.append("function networkmap_update(){return true;}")
    lines.append("function get_nmap_state(){return 0;}")
    lines.append("function getclients(a,b){")
    lines.append("  var list = [{}];")
    lines.append("  eval('ipmonitor = [' + ipmonitor_last + ']');")
    lines.append("  return ipmonitor.map(function(c, i){")
    lines.append("    var devtype = c.length > 5 ? c[5] : 0;")
    lines.append("    var wlenc   = c.length > 6 ? c[6] : 10;")
    lines.append("    var wlflag  = (wlenc == 10) ? 0 : 1;")
    lines.append("    return [c[0], c[1], c[2], c[3], c[4], devtype, wlflag, 'u'];")
    lines.append("  });")
    lines.append("}")
    lines.append("function get_ap_mode(){return (wan_route_x=='IP_Bridged'||sw_mode=='3');}")
    return "\n".join(lines)

# ============================================================
#  OpenSSL / OpenVPN 证书钩子
# ============================================================

def openssl_util_hook():
    return "var openssl_util_found = true;"

def openvpn_srv_cert_hook():
    return "var openvpn_srv_cert_found = true;"

def openssl_util_found():
    return True

def openvpn_srv_cert_found():
    return True

# ============================================================
#  start_apply.htm 表单处理
# ============================================================

def update_variables():
    """<% update_variables(); %> - 把 POST 表单字段写回 NVRAM"""
    from flask import request
    if request.method != "POST":
        return ""
    count = 0
    for key, val in request.form.items(multi=False):
        # 跳过 start_apply 内部字段
        if key in ("action_mode", "current_page", "next_page", "group_id",
                   "sid_list", "next_host", "flag", "action_script", "modified",
                   "action_mode"):
            continue
        val = val or ""
        # 点号表示 section.key
        if "." in key:
            _nv().set_flat(key, val)
        else:
            # 无点号 -> LANHostConfig 作为默认 section
            _nv().set("LANHostConfig", key, val)
        count += 1

    # 处理特殊字段组: help_enable_1 / help_enable_0
    for suf in ("1", "0"):
        field = f"help_enable_{suf}"
        if field in request.form:
            _nv().set("General", "help_enable", request.form[field])
            break

    return f"var page_modified = 1;"

def asus_nvram_commit():
    """<% asus_nvram_commit(); %>"""
    _nv().commit()
    return ""

def notify_services():
    """<% notify_services(); %>"""
    return ""

# ============================================================
#  其他
# ============================================================

def wol_action():
    """<% wol_action(); %>"""
    return ""

def get_vpns_client():
    """<% get_vpns_client(); %>"""
    return ""

# ============================================================
#  WiFi 硬件 / BSSID
# ============================================================

def wl_bssid_2g():
    return MAC_2G

def wl_bssid_5g():
    return MAC_5G

# ============================================================
#  网络接口
# ============================================================

def lanlink(*args):
    return ""

# ============================================================
#  WAN 动作
# ============================================================

def wan_action(*args):
    return ""

# ============================================================
#  带宽 / QoS
# ============================================================

def bandwidth(*args):
    return ""

def nf_values(*args):
    return ""

# ============================================================
#  系统日志 / MIB
# ============================================================

def dump_syslog(*args):
    return ""

def dump_eth_mib(*args):
    return ""

# ============================================================
#  下载 / 共享
# ============================================================

def create_account(*args): return ""
def delete_account(*args): return ""
def modify_account(*args): return ""
def get_all_accounts(*args): return ""
def get_permissions_of_account(*args): return ""
def set_account_permission(*args): return ""
def create_sharedfolder(*args): return ""
def delete_sharedfolder(*args): return ""
def modify_sharedfolder(*args): return ""
def get_share_tree(*args): return ""
def get_folder_tree(*args): return ""
def get_usb_share_list(*args): return ""
def set_share_mode(*args): return ""

# ============================================================
#  硬件 / 外设
# ============================================================

def hardware_pins(*args): return ""
def initial_account(*args): return ""
def safely_remove_disk(*args): return ""
def rules_count(*args): return ""

# ============================================================
#  AiDisk / 云服务
# ============================================================

def get_AiDisk_status(*args): return ""
def set_AiDisk_status(*args): return ""

# ============================================================
#  DNS 转发
# ============================================================

def dnsforwarder_status(*args): return ""

# ============================================================
#  OpenVPN CLI 证书
# ============================================================

def openvpn_cli_cert_hook():
    return "var openvpn_cli_cert_found = true;"

# ============================================================
#  第三方服务
# ============================================================

def shadowsocks_action(*args): return ""
def shadowsocks_status(*args): return ""
def scutclient_action(*args): return ""
def scutclient_status(*args): return ""
def scutclient_version(*args): return ""
def mentohust_action(*args): return ""
def mentohust_status(*args): return ""

# ============================================================
#  翻译占位符
# ============================================================

def translate_key(key, lang="EN"):
    """给 cgi_engine 调用的翻译"""
    cur = _nv().get("", "preferred_lang", "EN")
    return translate(key, cur)

# ============================================================
#  CGI 函数注册表
# ============================================================

CGI_FUNC_TABLE = {
    "nvram_get_x": nvram_get_x,
    "nvram_match_x": nvram_match_x,
    "nvram_dump": nvram_dump,
    "nvram_char_to_ascii": nvram_char_to_ascii,
    "nvram_double_match_x": nvram_double_match_x,
    "nvram_get_ddns": nvram_get_ddns,
    "nvram_get_table_x": nvram_get_table_x,
    "get_parameter": get_parameter,
    "get_flash_time": get_flash_time,
    "wanlink": wanlink,
    "detect_internet": detect_internet,
    "json_system_status": json_system_status,
    "uptime": uptime,
    "board_boot_time": board_boot_time,
    "netdev": netdev,
    "get_static_ccount": get_static_ccount,
    "get_static_client": get_static_client,
    "get_nvram_list": get_nvram_list,
    "wl_auth_list": wl_auth_list,
    "disk_pool_mapping_info": disk_pool_mapping_info,
    "available_disk_names_and_sizes": available_disk_names_and_sizes,
    "get_usb_ports_info": get_usb_ports_info,
    "get_ext_ports_info": get_ext_ports_info,
    "foreign_disks": foreign_disks,
    "foreign_disk_interface_names": foreign_disk_interface_names,
    "foreign_disk_model_info": foreign_disk_model_info,
    "foreign_disk_total_size": foreign_disk_total_size,
    "blank_disks": blank_disks,
    "blank_disk_total_size": blank_disk_total_size,
    "blank_disk_interface_names": blank_disk_interface_names,
    "wl_scan_2g": wl_scan_2g,
    "wl_scan_5g": wl_scan_5g,
    "wl_bssid_2g": wl_bssid_2g,
    "wl_bssid_5g": wl_bssid_5g,
    "shown_language_option": shown_language_option,
    "login_state_hook": login_state_hook,
    "login_safe": login_safe,
    "firmware_caps_hook": firmware_caps_hook,
    "openssl_util_hook": openssl_util_hook,
    "openvpn_srv_cert_hook": openvpn_srv_cert_hook,
    "openvpn_cli_cert_hook": openvpn_cli_cert_hook,
    "openssl_util_found": openssl_util_found,
    "openvpn_srv_cert_found": openvpn_srv_cert_found,
    "update_variables": update_variables,
    "asus_nvram_commit": asus_nvram_commit,
    "notify_services": notify_services,
    "wol_action": wol_action,
    "get_vpns_client": get_vpns_client,
    "lanlink": lanlink,
    "wan_action": wan_action,
    "bandwidth": bandwidth,
    "nf_values": nf_values,
    "dump_syslog": dump_syslog,
    "dump_eth_mib": dump_eth_mib,
    "create_account": create_account,
    "delete_account": delete_account,
    "modify_account": modify_account,
    "get_all_accounts": get_all_accounts,
    "get_permissions_of_account": get_permissions_of_account,
    "set_account_permission": set_account_permission,
    "create_sharedfolder": create_sharedfolder,
    "delete_sharedfolder": delete_sharedfolder,
    "modify_sharedfolder": modify_sharedfolder,
    "get_share_tree": get_share_tree,
    "get_folder_tree": get_folder_tree,
    "get_usb_share_list": get_usb_share_list,
    "set_share_mode": set_share_mode,
    "hardware_pins": hardware_pins,
    "initial_account": initial_account,
    "safely_remove_disk": safely_remove_disk,
    "rules_count": rules_count,
    "get_AiDisk_status": get_AiDisk_status,
    "set_AiDisk_status": set_AiDisk_status,
    "dnsforwarder_status": dnsforwarder_status,
    "shadowsocks_action": shadowsocks_action,
    "shadowsocks_status": shadowsocks_status,
    "scutclient_action": scutclient_action,
    "scutclient_status": scutclient_status,
    "scutclient_version": scutclient_version,
    "mentohust_action": mentohust_action,
    "mentohust_status": mentohust_status,
}