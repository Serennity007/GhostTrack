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
