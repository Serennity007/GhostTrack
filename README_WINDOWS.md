# GhostTrack Console 1.5.0 使用说明

## 安装与启动

下载 `GhostTrack-v1.5.0-Windows-x64.zip`，完整解压，运行 `GhostTrack/GhostTrack.exe`。Windows 10/11 x64，无需 Python、管理员权限或账号登录。不要单独复制 EXE，`_internal` 和 `assets` 是运行依赖。

## 公开资源查询（新增）

- **域名综合报告**：输入域名，一次并行获取 RDAP、DNS、HTTPS 三类结果。每个来源保留独立字段、状态和来源链接；一个来源失败不影响其余结果。进度来自实际返回的来源。
- **域名档案**：输入已注册的域名，如 `example.com`，获取 RDAP 公开注册元数据。子域名通常没有独立注册档案。
- **DNS 记录**：输入域名，并行查询 A、AAAA、CNAME、MX、NS、TXT、SOA、CAA，保留 TTL。每类最多展示20条、6000字符，超出会标记截断，可打开来源核实。无记录显示 `—`，不存在显示 `NXDOMAIN`，请求失败显示 `ERROR` 并标记部分不可用。
- **网站与证书**：输入域名或 HTTPS URL，读取响应、标题、跳转链、公开响应头及证书。只连接公网443，最多4次请求，读取有限大小内容；TLS 验证失败会停止。支持声明 charset 的页面标题以及 gzip/deflate 压缩内容；解压和读取均限长，截断和不支持编码会明确标记。
- **IP / ASN 注册**：输入公网 IPv4/IPv6 或 `AS15169`，查看注册范围、CIDR、网络名称/标识和公开日期；不是终端用户身份。
- **GitHub 公开资料**：输入用户名或 `https://github.com/用户名`，读取公开简介、仓库/粉丝/关注计数和最近5个公开仓库。匿名 API 限流时保留已取得的部分结果，不要求填入登录凭据。

网站模块默认使用系统解析；若所有答案均来自本地代理常用的 198.18/15 Fake-IP 池，会改查 Google Public DNS，验证公网后连接真实地址。私网/回环混合解析仍会拒绝。直接 TLS 连接可能不适用于只开放显式 HTTP 代理的网络。

模块编号、字段数量和耗时来自实际运行状态；雷达图形为装饰，不表示扫描目标或已取得数据。

## 国内平台查询

| 平台 | 接受的输入 | 备注 |
|---|---|---|
| 抖音 | `https://www.douyin.com/user/…`、对应用户标识、`v.douyin.com` 主页分享短链 | 不是抖音号；视频链接不能当作主页 |
| 小红书 | `https://www.xiaohongshu.com/user/profile/…`、24位十六进制用户ID、`xhslink.com` 主页分享短链 | 保留公开分享链接需要的 xsec 参数；笔记不是主页 |
| 快手 | `https://www.kuaishou.com/profile/…` 或主页标识 | 不按昵称搜索 |
| B站 | 数字 UID、`https://space.bilibili.com/…` | 不是昵称 |
| 微博 | 数字 UID、`https://weibo.com/u/…` | 登录跳转会显示受限 |
| 知乎 | `https://www.zhihu.com/people/…` 或主页标识 | 不是显示昵称 |
| 豆瓣 | `https://www.douban.com/people/…` 或主页标识 | 不是显示昵称 |

粘贴链接可自动识别平台，也可粘贴含一个链接的完整分享文案；输入裸 ID 时需要先选具体平台。一次只接收一个链接。短链只沿所属平台已列出的官方域名展开，最多4次；禁止跳转到任意外部地址。短链过期或需脚本时，请自行在浏览器打开，再复制完整主页地址。

公开页面提供什么就显示什么。当前查询读取标题和简介，不承诺取得粉丝数、作品列表、联系方式、私密资料或账号实名。遇到 403、412、429、登录、验证、跳转或通用占位页时，保留主页链接并提示信息不足，不把它当作账号不存在。

## 结果与快捷键

- “填入示例”只填入当前模块的示例，不会自动查询。切换模块会清空当前视图，已完成查询仍可在会话历史中回看。
- Enter：查询；Esc：取消；Ctrl+L：输入框。
- 结果筛选框：按字段或内容过滤，不会删掉完整结果。
- 选中一行：下方滚动区显示完整文本。
- 双击结果行或 Ctrl+C：复制选中值。“复制全部”始终复制完整结果，不受筛选影响。
- “打开来源”：在默认浏览器打开平台主页。
- 导出 JSON / CSV / HTML，带查询工具、输入和 UTC 时间。CSV 为 UTF-8 BOM，防止公式文本被 Excel 直接执行；HTML 报告离线可读。

## 历史与设置

默认历史只保留当前会话，最多50条；持久化另有约1.9MB上限，优先保留最近结果。设置中可以开启“重启后保留查询历史”，仅保存到本机。历史窗口双击可查看旧结果；若要重新获取数据，恢复后再点击查询。“清空历史”会清除会话及已持久化的历史。

数据目录：`%LOCALAPPDATA%\GhostTrackDesk`。`state.json` 包含语言、默认地区和已启用保存的历史；`application.log` 为有大小限制的错误日志，不写入查询内容。也可用环境变量 `GHOSTTRACK_DATA_DIR` 指定测试/便携数据目录。历史中的分享链接可能含公开分享访问参数，请按需清空。

## 常见问题

- **只返回登录/验证/访问限制**：平台当前没有提供可直接读取的公开 HTML。使用“打开来源”自行查看；程序不绕过验证。
- **抖音号查不到**：使用主页 `/user/…` 链接或主页分享链接，显示抖音号不是该 URL 中的用户标识。
- **小红书链接失效**：重新从个人主页复制分享链接；笔记 `/explore/…` 链接暂不支持。分享参数可能过期。
- **取消后提示请求仍在结束**：窗口已取消显示和保存；正在进行的网络读操作会在超时后退出。为防止堆积，最多同时保留两次网络任务。
- **查询失败**：检查输入、网络和第三方服务；结果访问状态与账号存在性不同。
- **设置不能保存**：本次会话仍可用。检查数据目录的写入权限或指定可写的 `GHOSTTRACK_DATA_DIR`。
- **EXE 无法打开**：确认 Windows x64，并解压完整目录；本包未签名。不要删除 `_internal`。仍有问题可在仓库提交系统版本、应用版本和复现步骤，不要上传令牌、私密链接或个人历史。

## 源码和构建

运行环境 Python 3.11 x64。依赖在 `requirements.txt`，构建依赖在 `requirements-build.txt`。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

输出 `dist/v1.5.0/GhostTrack/`、`dist/GhostTrack-v1.5.0-Windows-x64.zip`、`dist/SHA256SUMS-v1.5.0.txt`。用 PowerShell `Get-FileHash` 对照 SHA256 校验文件。

## Languages

English: choose a tool, paste a profile URL/share message and press Enter. Ctrl+C copies a selected value; JSON/CSV/HTML export is available. History is session-only unless enabled in Settings. Access restrictions do not prove that an account does not exist.

日本語：ツールを選択し、プロフィール URL・共有文を貼り付けて Enter。選択行は Ctrl+C でコピーできます。JSON/CSV/HTML の保存に対応。履歴は既定で今回のセッションのみ。ログイン・検証が必要なページでは取得情報が制限されます。

Español: elige una herramienta, pega una URL de perfil o un mensaje compartido y pulsa Enter. Ctrl+C copia el valor seleccionado. Exportación JSON/CSV/HTML. Historial solo de la sesión por defecto; puedes activarlo en Ajustes. Las restricciones de acceso no confirman que una cuenta no exista.

基于 [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack)。原项目说明见 `UPSTREAM_README.md`。
