# Padavan WebUI Simulator

Flask 实现的 Padavan 路由器 WebUI 后端模拟器，用于在没有真实路由器的情况下调试
ASP 页面布局、JavaScript 交互、NVRAM 表单和 update.cgi 实时接口。

支持 Windows / Linux / macOS，可 `pyinstaller --onefile` 打成独立 exe。

## 目录结构

```
Padavan-WebUI-Simulator/
├─ run.py                 # 启动脚本
├─ _entry.py              # PyInstaller 打包入口
├─ requirements.txt       # Flask
└─ web_simulator/         # 核心包
   ├─ sim.py              # Flask 路由
   ├─ cgi_engine.py        # <% func() %> / <#dict#> 模板引擎
   ├─ padavan_funcs.py    # 所有 Padavan CGI 函数实现
   ├─ nvram.py            # NVRAM 模拟器
   ├─ dynstate.py         # WAN/流量/USB/系统状态模拟
   ├─ language.py         # dict 语言字典加载
   ├─ paths.py            # WWW 路径解析
   ├─ config.py           # 硬件参数 & 默认 NVRAM
   └─ __main__.py         # CLI 入口
```

## WWW 目录要求

```
<www>/
├─ n56u_ribbon_fixed/     # 所有 .asp .htm .js
└─ dict/                  # EN.header EN.footer CN.dict ...
```

## 运行

```bash
# 开发模式
pip install -r requirements.txt
python run.py --www ./www

# 或用模块方式
python -m web_simulator --www ./www --port 8080

# 参数
--www PATH      WWW 根目录 (默认找 ./www 或 PADAVAN_SIM_WWW 环境变量)
--host HOST     监听地址 (默认 0.0.0.0)
--port PORT     监听端口 (默认 8080)
--debug         Flask debug 模式
```

访问 `http://127.0.0.1:8080/`，账号密码 `admin / admin`。

## 打包 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --name padavan-sim _entry.py
# 产物在 dist/padavan-sim.exe
```

exe 默认查找**同目录下的 `./www`**，也可以 `padavan-sim.exe --www D:\my-www`。
