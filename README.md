# GhostTrack Console

四语言 Windows / Android 公开信息控制台：11 个查询模块，黑绿终端风格、编号导航、等宽结果区和真实查询耗时，基于 [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) 扩展。

[Android 安装与使用](README_ANDROID.md) · [下载 Windows 版](https://github.com/Serennity007/GhostTrack/releases/latest) · [使用说明](README_WINDOWS.md) · [更新记录](CHANGELOG.md) · [原项目说明](UPSTREAM_README.md)

## 快速开始

1. 在 Release 下载 `GhostTrack-v1.5.0-Windows-x64.zip`。
2. 解压整个文件夹，运行其中的 **GhostTrack.exe**，无需安装 Python。
3. 选择查询工具；国内平台可粘贴主页链接或分享文案，按 Enter 查询。

Windows 10/11 x64。便携包未签名，目录内的 `_internal` 文件夹是运行依赖，不能单独移走 EXE。

## 可以做什么

| 工具 | 输入 | 结果 |
|---|---|---|
| 域名综合报告 | 域名 | 并行汇总 RDAP、8类 DNS、网站与 TLS，分别标注来源状态 |
| 域名档案 | 域名 | 注册商、注册/到期/更新时间、DNSSEC、名称服务器 |
| DNS 记录 | 域名 | A / AAAA / CNAME / MX / NS / TXT / SOA / CAA |
| 网站与证书 | 公网 HTTPS 网址 | 响应状态、标题、跳转链、公开响应头、证书颁发者/有效期/SAN |
| IP / ASN 注册 | 公网 IP 或 AS15169 | 注册范围、CIDR、网络名称、注册国家代码 |
| GitHub 公开资料 | 用户名或主页 URL | 公开简介、计数、注册时间、最近5个公开仓库 |
| 国内公开主页 | 主页 URL / 分享文案 / 对应平台的用户 ID | 可读取的标题、简介、HTTP 状态、来源和查询时间 |
| IP 归属地 | 公网 IPv4 / IPv6 | 国家、地区、城市、经纬度估算、ASN、网络组织、服务商和时区 |
| 本机公网 IP | 无需输入 | 当前出口公网 IP |
| 号码元数据 | 电话号码，可选默认地区 | 号码段归属地、运营商、时区、国际格式和有效性 |
| 用户名链接 | 用户名 | GitHub、Instagram、X 的公开主页链接，未验证账号存在 |

支持 **抖音、小红书、快手、B站、微博、知乎、豆瓣**。识别主页链接和分享文案，支持抖音/小红书主页短链的有限跳转解析。视频、笔记、登录页和昵称反查不在当前支持范围。抖音主页标识与“抖音号”不同，请优先粘贴主页链接。

平台可能要求登录、验证或 JavaScript；这时显示受限状态，保留可复制、可在浏览器中打开的链接。不会把 HTTP 200 当作账号或身份已确认，也不会凭空补全粉丝数等字段。

## 日常使用

- 示例一键填入（不会自动发出请求）、模块来源标识、真实耗时与结果字段统计。
- 简体中文 / English / 日本語 / Español 即时切换，记住语言和默认号码地区。
- 复制单个值或全部结果；选中行后双击 / Ctrl+C。
- 筛选结果字段与内容，查看完整值；打开来源核实。
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

公开资源使用 RDAP 注册服务、Google Public DNS、GitHub 公共 API；网站模块直接读取用户输入的公网 HTTPS 网址。IP 归属地使用 ipwho.is，公网 IP 使用 api.ipify.org；主页查询访问相应平台。号码解析在本地完成。号码段信息和 IP 数据库位置均非实时设备位置。

原命令行入口 `GhostTR.py` 保留。原作者为 HunxByts；本仓库不是各平台官方客户端。具体使用和故障排查见 [Windows 使用说明](README_WINDOWS.md)。

## 公开来源与服务限制

- [RDAP 服务](https://about.rdap.org/)：域名、IP/ASN 的公开注册元数据，不导出注册人联系信息。
- [Google DNS JSON API](https://developers.google.com/speed/public-dns/docs/doh/json)：8类 DNS 记录；网站模块遇到本地代理的 198.18/15 Fake-IP 池时，使用公网 DoH 答案并验证其为公网后连接。
- [GitHub 用户接口](https://docs.github.com/en/rest/users/users#get-a-user)：匿名公开资料和最近公开仓库；不读取私有数据或邮箱，不使用本机 gh 登录令牌。限流时标记部分来源不可用。
- 网站仅支持 HTTPS 默认443端口。逐次验证解析地址并固定公网连接地址，保留 TLS 主机名校验；不访问内网、回环和保留目标，不绕过证书错误。该模块使用直接 TLS 连接，某些仅支持显式 HTTP 代理的网络可能无法访问。

公开来源有各自的可用性、限流和字段差异；结果不会补造缺失内容。没有手机号到私人平台账号的反查或身份关联。
