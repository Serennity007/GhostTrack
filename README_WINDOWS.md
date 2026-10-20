# GhostTrack Windows 中文版 1.0.0

基于 [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) 的独立桌面入口，保留原作者署名与原命令行程序。

## 使用

下载 Release 中的 `GhostTrack-Windows-x64.zip`，解压后双击 `GhostTrack.exe`。无需安装 Python，适用于 Windows 10/11 x64。

- 中文图形界面，后台查询不会阻塞窗口。
- 查询公网 IPv4/IPv6 的估算归属地、查看本机公网 IP。
- 离线解析号码段归属地、运营商、格式和有效性；无国际区号时可选择地区，默认 CN。
- 生成 GitHub、Instagram、X 公开用户名链接，不声称已核实账号存在或身份。
- 复制结果，导出 UTF-8 JSON 或兼容 Excel 的 CSV。
- 输入验证、HTTPS、15 秒网络超时及错误提示。

IP 查询会向 ipwho.is 发送所输入的 IP，本机公网 IP 使用 api.ipify.org。号码解析和用户名链接生成在本地完成。归属地数据不提供实时定位。

## 从源码运行和构建

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe -m pip install pyinstaller==6.22.3
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name GhostTrack --collect-all phonenumbers desktop.py
```

构建输出在 `dist/GhostTrack/`，分发时需保留整个文件夹。此版本为未签名的便携程序。

## 1.1.0 International / 国际版

- 简体中文、English、日本語、Español 即时切换；工具、状态、错误提示、字段、复制及导出随界面语言变化。
- 深色工作台、侧边导航、青绿色操作按钮、结构化结果表格；选中一行可查看完整字段值。
- 查询期间可继续切换语言。电话号码地域描述按发起查询时的语言生成；若需更换该内容语言，请重新查询。外部服务返回的国家/城市名称保留原始数据。
- 新包名 `GhostTrack-International-Windows-x64.zip`，解压后运行 `GhostTrack-International.exe`。
- 构建命令使用 `--name GhostTrack-International`；测试命令：`.\.venv\Scripts\python.exe -m unittest test_desktop -v`。

## 1.2.0 国内公开主页与快捷复制

- 国内平台：B站（Bilibili）、微博（Weibo）、知乎（Zhihu）、豆瓣（Douban）。B站/微博输入数字 UID，知乎/豆瓣输入主页标识；也可粘贴平台的标准 HTTPS 主页链接。不是按昵称跨平台匹配身份。
- 查询公开 HTML 的标题和简介，附带来源链接、UTC 查询时间和 HTTP 状态。登录、验证、跳转、访问限制、缺少元信息时显示账号状态未知，并保留可打开/复制的主页链接。
- 不登录、不读取浏览器 Cookie、不绕过验证；不依据 HTTP 200 推断账号存在。平台是否提供公开内容由网站决定。
- 复制全部；选中一行后复制该值，支持双击和 Ctrl+C。主页结果可直接在默认浏览器中打开。
- 四语言提示与导出继续支持；修复小窗口中底部按钮被结果区域挤出的布局问题。
- 新包 `GhostTrack-v1.2.0-Windows-x64.zip`，解压整个目录运行 `GhostTrack-v1.2.0.exe`。
- 测试：`.\.venv\Scripts\python.exe -m unittest test_desktop test_platforms -v`
- 构建：`.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name GhostTrack-v1.2.0 --collect-all phonenumbers desktop.py`
