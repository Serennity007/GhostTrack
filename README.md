# GhostTrack Console

**简体中文** · [English](README.en.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Français](README.fr.md)

面向 Windows 与 Android 的公开信息查询控制台。12 个 Windows 工具与 11 个 Android 模块共享查询服务，以深色控制台、清晰的来源状态和可导出的结果，集中查看域名、DNS、网站证书、网络注册与公开主页信息。

> 文档提供中、英、日、西、法五种语言；应用界面支持简体中文、English、日本語、Español 四种语言。

## 下载与安装

| 平台 | 下载 v1.7.0 | 安装方法 |
|---|---|---|
| Windows 10/11 x64 | [便携 ZIP](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.7.0/GhostTrack-v1.7.0-Windows-x64.zip) · [发布说明与 SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/windows-v1.7.0) | 完整解压，运行 `GhostTrack/GhostTrack.exe` |
| Android 7.0+ | [通用 APK](https://github.com/Serennity007/GhostTrack/releases/download/android-v1.6.0/GhostTrack-v1.6.0-Android-universal.apk) · [发布说明与 SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0) | 在手机文件管理器中打开 APK 安装 |

Windows 无需安装 Python；请保留 EXE 所在文件夹及其依赖，不要单独移动 EXE。Android 包支持 ARM64、ARMv7 和 x86_64，首次启动会解压内置运行环境；只给实际用于打开 APK 的应用授予安装来源权限。后续更新请使用本仓库以同一证书签名的 APK。

[Windows 使用说明](README_WINDOWS.md) · [Android 使用与构建](README_ANDROID.md) · [更新记录](CHANGELOG.md)

## 界面

![Windows 公开信息控制台](docs/desktop.png)

<img src="docs/android.png" width="320" alt="Android 公开信息控制台" />

界面提供编号导航、来源标识、查询耗时和字段数量。装饰图形不表示正在扫描目标；查询状态与结果来自实际返回的数据。

## 12 个查询工具

| 工具 | 输入 | 可取得的公开信息 |
|---|---|---|
| 授权账号档案 | 电话号码或关键词 | 本机保存的授权号码与主页关联、来源与保存时间 |
| 域名综合报告 | 域名 | 并行汇总 RDAP、DNS、HTTPS，各来源独立标记状态 |
| 域名档案 | 域名 | 注册商、注册/到期/更新日期、DNSSEC、名称服务器 |
| DNS 记录 | 域名 | A、AAAA、CNAME、MX、NS、TXT、SOA、CAA 与 TTL |
| 网站与证书 | 公网 HTTPS 网址 | HTTP 状态、标题、跳转、公开响应头、TLS 颁发者/有效期/SAN |
| IP / ASN 注册 | 公网 IP 或 `AS15169` | 注册范围、CIDR、网络名称、注册国家代码与日期 |
| GitHub 公开资料 | 用户名或主页 URL | 公开简介、计数、注册日期、最近 5 个公开仓库 |
| 国内公开主页 | 主页 URL、分享文案或平台用户 ID | 可读取的页面标题、简介、访问状态、来源和查询时间 |
| IP 归属地 | 公网 IPv4 / IPv6 | 数据库估算地区、网络组织、服务商、ASN 和时区 |
| 本机公网 IP | 无需输入 | 当前网络出口的公网 IP |
| 号码元数据 | 电话号码与默认地区 | 本地解析号码段归属地、运营商、时区、格式和有效性 |
| 用户名链接 | 用户名 | 生成 GitHub、Instagram、X 主页链接，不验证账号存在 |

国内平台支持 **抖音、小红书、快手、B站、微博、知乎、豆瓣**。建议粘贴完整个人主页链接；支持部分抖音、小红书主页分享短链。显示昵称、“抖音号”、视频或笔记链接不能替代对应的主页标识。

## 结果处理

- 示例一键填入，不自动发起请求；可取消查询并忽略迟到响应。
- 按字段或内容筛选，查看完整值，复制单项或全部结果，打开来源核实。
- 导出 JSON、UTF-8 BOM CSV、离线 HTML，附查询工具、输入和 UTC 时间；CSV 包含公式文本保护。
- Windows 支持双击 / Ctrl+C 复制、Enter 查询、Esc 取消；Android 支持触屏复制与系统文件选择器导出。
- Windows 会话历史最多 50 条，默认不跨会话保存，可在设置中开启本机保存；Android 不持久保存查询历史，仅记住语言和模块。
- 平台查询结果可一键「存入档案」：保存本人授权或对方公开的电话号码与主页关联（含来源与保存时间），侧栏「档案管理」支持删除与导出，模块 12 可按号码或关键词在本机档案中查找。

## 数据来源与限制

查询访问 [RDAP](https://about.rdap.org/)、[Google Public DNS](https://developers.google.com/speed/public-dns/docs/doh/json)、[GitHub 公共 API](https://docs.github.com/en/rest/users/users#get-a-user)、ipwho.is、api.ipify.org，以及输入的公开网站或平台主页。联网模块会把查询目标发送给相应服务；号码元数据在本地解析。没有项目中转服务器、账号登录或统计遥测。

平台登录、验证码、JavaScript、限流或服务故障可能限制结果。程序保留已取得的数据及来源状态，不绕过访问控制，也不将 HTTP 200 当作身份已验证。网站模块只读取公网 HTTPS 默认 443 端口，验证证书并限制跳转与内容大小。缺失字段不会补造；RDAP 不导出注册人联系信息。

**号码段与 IP 数据库位置不是设备实时位置。没有手机号反查私人平台账号、实名识别或跨平台身份关联功能；授权账号档案只保存你主动提供并声明来源的关联，仅存放在本机，可随时删除。** 仅查询你有权访问的公开信息，并遵守来源服务的使用规则。

Windows 设置与可选历史位于 `%LOCALAPPDATA%\GhostTrackDesk`，可在应用中清空历史；错误日志不记录查询内容。Android 仅申请联网权限，不申请定位、通讯录、短信、电话或整盘存储权限。导出文件、剪贴板与分享链接可能含查询内容，请自行管理。

## 开发与构建

Python 3.11 x64，Windows 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

Android 需要 JDK 17 与 Android SDK Platform 36 / Build Tools 36.0.0，仓库包含 Gradle Wrapper：

```powershell
$env:JAVA_HOME = '你的 JDK 17 目录'
$env:ANDROID_HOME = '你的 Android SDK 目录'
.\.venv\Scripts\python.exe build_android.py --gradle .\android\gradlew.bat
```

构建脚本运行测试、生成发布包与 SHA256；Android 另运行 Lint 并验证签名。签名密钥位于仓库外，备份方法见 [Android 构建说明](README_ANDROID.md)。不要将私钥或凭据提交到 Git。Windows 自动构建模板见 [工作流示例](docs/windows-workflow.example.yml)；提供模板不代表已启用线上 CI。

## 来源与反馈

基于 [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) 扩展，保留原命令行入口 `GhostTR.py` 与[原项目说明](UPSTREAM_README.md)。本项目不是所查询平台的官方客户端。

遇到问题请在 [Issues](https://github.com/Serennity007/GhostTrack/issues) 提供系统版本、应用版本和复现步骤，不要上传令牌、私钥、个人历史或私密链接。
