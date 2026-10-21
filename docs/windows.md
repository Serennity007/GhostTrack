# Windows guide

[English home](../README.md) · [中文使用说明](../README_WINDOWS.md) · [Android guide](android.md) · [Changelog](../CHANGELOG.md)

GhostTrack Console for Windows provides 12 tools in a desktop workbench: public-data queries, report export, and a local archive of account associations you supply. The current Windows release is **1.8.0**. The interface supports English, Simplified Chinese, Japanese, and Spanish; French is available in the repository documentation.

![GhostTrack 1.8.0 Windows workbench in English](screenshots/windows-overview-en.jpg)

## Install

1. Download [GhostTrack-v1.8.0-Windows-x64.zip](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.8.0/GhostTrack-v1.8.0-Windows-x64.zip) and its [SHA256 file](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.8.0/SHA256SUMS-v1.8.0.txt).
2. Extract the **entire ZIP** to a folder you can write to.
3. Open `GhostTrack/GhostTrack.exe`.

Use Windows 10 or 11 x64. You do not need Python, administrator access, or an application account. Keep the EXE with the supplied `_internal` directory and other bundled files. This release does not include a Windows code-signing certificate.

Check the ZIP before extracting it:

```powershell
Get-FileHash .\GhostTrack-v1.8.0-Windows-x64.zip -Algorithm SHA256
Get-Content .\SHA256SUMS-v1.8.0.txt
```

Compare the complete hash values. A checksum confirms that your download matches the release asset.

## First query

Choose **Domain overview**, enter `python.org`, and select **Query**. The application requests RDAP, DNS, and HTTPS data in parallel. Each source has its own fields and status; you can keep the other results if one source fails.

Use the language selector to choose English. **Example** fills a sample input without sending a request. The left pane holds the query and source information; the right pane holds the results, filter, full-value detail, and export actions. The metric cards show the current field count and elapsed time.

## Tools and inputs

| Tool | Example input | What you receive |
| --- | --- | --- |
| Domain overview | `python.org` | Combined RDAP, DNS, and HTTPS/TLS report with per-source status |
| Domain registration | `example.com` | Public RDAP registration metadata and dates; registrant contact details are excluded |
| DNS records | `example.com` | A, AAAA, CNAME, MX, NS, TXT, SOA, and CAA records with TTL |
| Website and certificate | `https://www.python.org/` | HTTP response, page title, redirect chain, selected headers, and TLS certificate metadata |
| IP / ASN registration | `8.8.8.8`, `AS15169` | Public network registration, address ranges, CIDR, identifiers, and dates |
| IP location | `8.8.8.8` | Provider database estimates for region, network organization, ISP, ASN, and time zone |
| My public IP | No input | The public address visible to the IP service |
| Phone metadata | `+12025550123` | Number formats, validity, numbering region, carrier metadata, and time zones |
| Username links | `octocat` | Candidate profile links for GitHub, Instagram, and X; no existence check |
| GitHub public profile | `octocat` or a GitHub profile URL | Public profile fields, repository/follower/following counts, and five recent public repositories |
| Chinese platforms | `https://space.bilibili.com/2` | A normalized profile URL, readable public HTML metadata, and access status |
| Authorized account archive | A saved phone fragment or keyword | Matches from associations you have saved on this computer |

Phone metadata runs against the bundled `phonenumbers` database. For a national-format number, choose the corresponding two-letter region code, such as `US`, `CN`, or `JP`. International `+` format avoids ambiguity. Numbering metadata and IP database estimates do not locate a device in real time.

For domain registration, enter a registered domain; a subdomain usually has no separate RDAP registration. DNS results include up to 20 records and 6,000 characters per record type. The application marks truncation, absent records, `NXDOMAIN`, and failed requests separately.

## Chinese public profiles

| Platform | Accepted profile input | Input detail |
| --- | --- | --- |
| Douyin | `https://www.douyin.com/user/…`, the corresponding user identifier, or a supported `v.douyin.com` profile share link | A displayed Douyin handle is not the URL identifier |
| Xiaohongshu | `https://www.xiaohongshu.com/user/profile/…`, a 24-character hexadecimal user ID, or a supported `xhslink.com` profile share link | Preserve required public `xsec` share parameters |
| Kuaishou | `https://www.kuaishou.com/profile/…` or the profile identifier | Use an identifier rather than a display name |
| Bilibili | Numeric UID or `https://space.bilibili.com/…` | Use the UID rather than a nickname |
| Weibo | Numeric UID or `https://weibo.com/u/…` | A login redirect may limit the result |
| Zhihu | `https://www.zhihu.com/people/…` or the profile identifier | Use the URL identifier |
| Douban | `https://www.douban.com/people/…` or the profile identifier | Use the URL identifier |

Choose **Auto** for a supported full URL or paste a share message containing one URL. Select a specific platform before using a bare ID. Video, note, and post links are not profile inputs. The application expands supported short links only through the platform's listed official hosts, with a four-request limit. If a link expires or requires JavaScript, open it in your browser and copy the final profile URL.

These queries read page titles and descriptions when the public HTML provides them. They do not promise follower counts, post lists, contact details, or verified identity. A login page, CAPTCHA, rate limit, generic placeholder, or HTTP restriction means the program has insufficient information; it does not establish that an account is absent.

## Copy, filter, and export

| Action | Control |
| --- | --- |
| Run a query | Enter or **Query** |
| Cancel the current query | Esc or **Cancel** |
| Focus the input | Ctrl+L |
| Read a complete value | Select its result row; use the detail pane |
| Copy a selected value | Double-click the row or press Ctrl+C |
| Copy the complete result | **Copy all**, including fields hidden by a filter |
| Filter the current view | Type a field name or value in the result filter |
| Inspect the source | **Open source** in your default browser |
| Save a report | **Export** and choose JSON, CSV, or HTML |

Reports include the query tool, input, and UTC timestamp. CSV uses UTF-8 with a BOM and protects formula-like cell values. HTML reports open offline. Switching tools clears the current view; completed queries remain available in session history.

Cancellation stops the result from updating the interface or history. An existing network read can take until its timeout to finish. The application allows at most two outstanding network tasks to prevent a backlog.

## Local authorized account archive

From a Chinese platform result, choose **Save to archive** to record a phone/profile association you already know. You must declare one of two sources: **your own authorized information**, or **a phone number that the profile owner published on their public page**. The declaration records your stated source; the application does not verify consent or the association online.

Phone numbers normalize to E.164; profile URLs must match the selected platform. Saving the same phone/platform/profile combination updates that record. The archive holds up to 200 records, including the source, save time, and an optional note.

Search the archive by keyword or a phone digit fragment of at least three digits. The query view shows up to 12 matching records; **Manage archive** lets you review, delete, or export all records. The archive is a local record of what you supplied, not a phone-to-account discovery service.

## Storage and privacy

The default data directory is `%LOCALAPPDATA%\GhostTrackDesk`:

| File | Contents |
| --- | --- |
| `state.json` | Language, default phone region, and query history only if you enable persistence |
| `archive.json` | Your saved account associations, independently of query history |
| `application.log` | A bounded error log containing exception types rather than query contents |

History starts as session-only and holds up to 50 entries. Enable **Keep history after restart** in Settings if you want local persistence; the saved history also has an approximately 1.9 MB limit. Clear History removes session and persisted query history. It does not remove archive records; delete those in Manage archive. Share URLs may contain public access parameters, so review exports and stored history before sharing them.

Set `GHOSTTRACK_DATA_DIR` to use a different writable data directory:

```powershell
$env:GHOSTTRACK_DATA_DIR = 'C:\Users\YOUR_NAME\GhostTrack-data'
.\GhostTrack.exe
```

Queries contact the relevant public providers directly. The project does not operate a query relay server or ask for service tokens. Third-party providers receive the request and target you query.

## Network limits and troubleshooting

- **Website input rejected:** use a public HTTPS domain or URL on port 443, without credentials or fragments. Private, loopback, and mixed public/private resolutions are refused.
- **TLS error:** check the hostname, certificate, clock, and network. The website client preserves hostname checks and does not ignore invalid certificates.
- **Explicit proxy required:** the website module uses a direct TLS connection to a validated address. Networks that require an explicit HTTP proxy may not support this module. If every system DNS answer belongs to the `198.18.0.0/15` Fake-IP pool, the client tries Google Public DNS and validates the returned public addresses.
- **Partial report:** inspect each source status and source link. Provider downtime, anonymous API limits, and access restrictions can affect individual sources.
- **Douyin or Xiaohongshu lookup fails:** copy a current profile share URL, rather than a displayed handle, video, or note link.
- **Cannot save settings or reports:** choose a writable folder. Check `GHOSTTRACK_DATA_DIR` if you set it.
- **EXE cannot start:** confirm Windows x64 and extract the full archive. Include your OS version, app version, and reproduction steps in a [bug report](https://github.com/Serennity007/GhostTrack/issues/new/choose); remove personal results and private links first.

The website module follows at most four requests and bounds response reads and gzip/deflate decompression. It reports truncated or unsupported content. Decorative graphics do not indicate scanning activity.

## Run and build from source

Use **Python 3.11 x64 on Windows**. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

`requirements-build.txt` includes the shared dependencies and pinned PyInstaller tools. The build script runs the test suite, generates the icon and Windows version resource, bundles the application, and writes:

```text
dist/v1.8.0/GhostTrack/
dist/GhostTrack-v1.8.0-Windows-x64.zip
dist/SHA256SUMS-v1.8.0.txt
```

Versioned output folders allow a new build while an older version remains open. [`docs/windows-workflow.example.yml`](windows-workflow.example.yml) is a workflow template; this repository does not currently enable a GitHub Actions release workflow.

See the [contribution guide](../CONTRIBUTING.md) before changing query behavior or adding a provider. The [original upstream README](../UPSTREAM_README.md) documents the source project by [HunxByts](https://github.com/HunxByts/GhostTrack).
