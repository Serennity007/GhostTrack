# GhostTrack Desktop

四语言 Windows 公开信息查询工作台，基于 [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) 扩展。

[下载 Windows 版](https://github.com/Serennity007/GhostTrack/releases/latest) · [使用说明](README_WINDOWS.md) · [更新记录](CHANGELOG.md) · [原项目说明](UPSTREAM_README.md)

![GhostTrack Desktop 实际界面](docs/desktop.png)

## 快速开始

1. 在 Release 下载 `GhostTrack-v1.3.0-Windows-x64.zip`。
2. 解压整个文件夹，运行其中的 **GhostTrack.exe**，无需安装 Python。
3. 选择查询工具；国内平台可粘贴主页链接或分享文案，按 Enter 查询。

Windows 10/11 x64。便携包未签名，目录内的 `_internal` 文件夹是运行依赖，不能单独移走 EXE。

## 可以做什么

| 工具 | 输入 | 结果 |
|---|---|---|
| 国内公开主页 | 主页 URL / 分享文案 / 对应平台的用户 ID | 可读取的标题、简介、HTTP 状态、来源和查询时间 |
| IP 归属地 | 公网 IPv4 / IPv6 | 国家、地区、城市、经纬度估算和服务商 |
| 本机公网 IP | 无需输入 | 当前出口公网 IP |
| 号码元数据 | 电话号码，可选默认地区 | 号码段归属地、运营商、时区、国际格式和有效性 |
| 用户名链接 | 用户名 | GitHub、Instagram、X 的公开主页链接，未验证账号存在 |

支持 **抖音、小红书、快手、B站、微博、知乎、豆瓣**。识别主页链接和分享文案，支持抖音/小红书主页短链的有限跳转解析。视频、笔记、登录页和昵称反查不在当前支持范围。抖音主页标识与“抖音号”不同，请优先粘贴主页链接。

平台可能要求登录、验证或 JavaScript；这时显示受限状态，保留可复制、可在浏览器中打开的链接。不会把 HTTP 200 当作账号或身份已确认，也不会凭空补全粉丝数等字段。

## 日常使用

- 简体中文 / English / 日本語 / Español 即时切换，记住语言和默认号码地区。
- 复制单个值或全部结果；选中行后双击 / Ctrl+C。
- 筛选结果字段与内容，查看完整值；打开主页核实。
- JSON、Excel 兼容 CSV、独立 HTML 报告导出，附查询输入、工具和 UTC 时间。
- 可取消查询，忽略迟到响应；会话历史最多 50 条，支持回看和清空。
- 历史默认不跨会话保存，可在设置中开启本机保存。
- 使用帮助、错误提示、滚动长文本、窗口布局适配、应用图标和版本信息。

## 开发与构建

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe build_windows.py
```

构建脚本先运行测试，再打包 EXE，生成 ZIP 和 SHA256 校验文件。`docs/windows-workflow.example.yml` 提供 Windows GitHub Actions 模板；本次登录令牌没有 workflow 权限，未启用线上自动构建。具备权限时可将模板放到 `.github/workflows/windows.yml`。

## 数据与边界

数据保存在 `%LOCALAPPDATA%\GhostTrackDesk`。历史仅在用户开启后写入本机，含分享链接和查询结果，可清空。分享链接中的公开访问参数可能保留，以便平台正常打开。错误日志不记录查询内容。没有统计上报、账号登录或后台遥测。

IP 归属地使用 ipwho.is，公网 IP 使用 api.ipify.org；主页查询访问相应平台。号码解析在本地完成。号码段信息和 IP 数据库位置均非实时设备位置。

原命令行入口 `GhostTR.py` 保留。原作者为 HunxByts；本仓库不是各平台官方客户端。具体使用和故障排查见 [Windows 使用说明](README_WINDOWS.md)。
