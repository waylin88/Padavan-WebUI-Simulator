# -*- coding: utf-8 -*-
"""Padavan 模板引擎 - 解析 <% func(...) %> 和 <#dict_key#>"""

import re
import sys
from .padavan_funcs import CGI_FUNC_TABLE, translate_key

# 匹配 <% ... %> 和 <#...#>
_RE_CGI = re.compile(r"""<%\s*(.+?)\s*%>""", re.DOTALL)
_RE_DICT = re.compile(r"""<#(.+?)#>""")

# 匹配相邻的两个字符串字面量（Padavan httpd 模板会在它们之间自动插入逗号）
_RE_NEIGHBOR_STR = re.compile(
    r"""("[^"\\]*(?:\\.[^"\\]*)*")\s+("[^"\\]*(?:\\.[^"\\]*)*")"""
)

def _parse_args(arg_str):
    """解析 Padavan CGI 参数字符串
    Padavan 同时支持逗号、空格、紧贴引号作为参数分隔符:
      nvram_get_x("" "sw_mode")      <- 逗号
      nvram_get_x("" "sw_mode")       <- 空格
      nvram_match_x(\'\'\'rt_radio_x\'\'\') <- 紧贴: "" + "rt_radio_x"
    """
    arg_str = arg_str.strip()
    if not arg_str:
        return []
    args = []
    depth = 0
    cur = []
    in_str = None
    i = 0
    while i < len(arg_str):
        c = arg_str[i]
        if in_str:
            cur.append(c)
            if c == in_str:
                in_str = None
                # 退出字符串后，若下一个非空字符是引号或裸词起始，立即分割
                j = i + 1
                while j < len(arg_str) and arg_str[j].isspace():
                    j += 1
                if j < len(arg_str):
                    nc = arg_str[j]
                    if nc in ('\"', "'") or nc.isalpha() or nc == '_' or nc.isdigit():
                        args.append("".join(cur).strip())
                        cur = []
            i += 1
            continue
        if c in ('\"', "'"):
            in_str = c
            cur.append(c)
            i += 1
            continue
        if c == '(' or c == '[':
            depth += 1
            cur.append(c)
            i += 1
            continue
        if c == ')' or c == ']':
            depth -= 1
            cur.append(c)
            i += 1
            continue
        if depth == 0:
            if c == ',':
                args.append("".join(cur).strip())
                cur = []
                i += 1
                continue
            if c.isspace():
                stripped_cur = "".join(cur).strip()
                if stripped_cur and i + 1 < len(arg_str) and not arg_str[i + 1].isspace():
                    args.append(stripped_cur)
                    cur = []
                    i += 1
                    continue
                i += 1
                continue
        cur.append(c)
        i += 1
    if cur:
        args.append("".join(cur).strip())
    return args

def _literalize(arg):
    """把字符串参数变成 Python 值"""
    if arg is None:
        return ""
    s = arg.strip()
    if (s.startswith('\"') and s.endswith('\"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    # 裸词 - 原样返回
    return s

def _eval_call(expr: str) -> str:
    """求值单个函数调用表达式 'nvram_get_x("a" "b")' -> '...'"""
    expr = expr.strip()
    # 特殊处理: <% 变量名 %> 不带括号 (极少)
    if "(" not in expr:
        if expr in CGI_FUNC_TABLE:
            return str(CGI_FUNC_TABLE[expr]())
        # 尝试作为 nvram_get_x("" expr)
        return ""

    # 提取函数名和参数: func_name(args...);
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*;?\s*$", expr, re.DOTALL)
    if not m:
        # 无法解析 -> 返回空
        return ""

    fname = m.group(1)
    raw_args = _parse_args(m.group(2))
    py_args = [_literalize(a) for a in raw_args]

    func = CGI_FUNC_TABLE.get(fname)
    if not func:
        # 未实现的函数 - 打印警告但返回空串
        print(f"[cgi_engine] 未实现的 CGI 函数: {fname}", file=sys.stderr)
        return ""

    try:
        result = func(*py_args)
        if result is None:
            return ""
        return str(result)
    except Exception as e:
        print(f"[cgi_engine] 执行 {fname}() 出错: {e}", file=sys.stderr)
        return f"/* ERR: {e} */"

def render(template: str) -> str:
    """渲染 Padavan 模板:
    1. 替换 <#key#> 为翻译
    2. 替换 <% func(args) %> 为 CGI 函数返回值
    3. 在 new Array(...) 内相邻字符串字面量之间自动插入逗号
       （Padavan httpd 模板引擎的隐式行为）"""
    # 先处理翻译（因为有些翻译值里不会有特殊语法冲突）
    result = _RE_DICT.sub(lambda m: translate_key(m.group(1)), template)
    # 再处理 CGI 函数
    result = _RE_CGI.sub(lambda m: _eval_call(m.group(1)), result)
    # 最后：循环在相邻字符串字面量之间插逗号，直到稳定
    prev = None
    while prev != result:
        prev = result
        result = _RE_NEIGHBOR_STR.sub(
            lambda m: m.group(1) + chr(44) + " " + m.group(2), result
        )
    return result
