# Privacy and data flow

[Project home](../README.md) · [Feature catalogue](FEATURES.md) · [Windows guide](windows.md) · [Android guide](android.md)

This document describes the current application code and the published Windows 1.9.0 / Android 1.6.0 behavior. GhostTrack sends public lookup requests from your device to the providers below. The project has no query relay server or application login, and the query tools do not ask for account credentials or API tokens.

## Where a query goes

| Action | Destination | Information sent |
| --- | --- | --- |
| IP location | `ipwho.is` | The target public IP in the request path |
| My public IP | `api.ipify.org` | An IP-detection request; the provider observes your connection's public address |
| Domain / IP / ASN registration | `rdap.org`, followed by the relevant registry's RDAP service | The domain, public IP, or ASN |
| DNS records | `dns.google` | The domain and requested record type |
| Website and certificate | The HTTPS target and allowed public HTTPS redirect destinations | Hostname, requested path and query string, and HTTP request headers |
| Website Fake-IP fallback | `dns.google`, only when all system answers are in `198.18.0.0/15` | The hostname and an A-record request |
| GitHub public profile | `api.github.com` | The username, then a request for five recently updated public repositories |
| Chinese public profile | The chosen platform's profile host; supported share hosts during short-link expansion | The profile identifier and required public share parameters |
| Domain overview | The RDAP, DNS, and HTTPS destinations above | The domain and corresponding source queries |
| Phone metadata | No lookup provider | The bundled `phonenumbers` database processes the number on your device |
| Username links | No lookup provider | The application generates URLs locally; opening one contacts that platform in your browser |
| Authorized archive | No lookup provider | Windows searches the records you saved locally |

A remote provider can see the request, its timing, and your connection address, subject to your network or proxy configuration. System DNS resolvers may also receive target hostname lookups. HTTPS protects the connection in transit; it does not hide a query from its destination. Provider retention and responses fall outside the application's local storage controls.

Chinese profile hosts are Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu, and Douban. The application permits only the listed official hosts for supported profile short links. On Windows, a browser you open through **Open source** uses its own cookies, account session, and settings; GhostTrack does not import that browser session.

## Windows local data

### Atlas browser workspace · 1.9.0

The local Atlas service binds to `127.0.0.1` only and checks Host, Origin and a per-process request token. It reuses the public query engine without exposing desktop history or the authorized archive. It records no query database or request log. Closing the desktop stops its owned local service.

Atlas results and queued reports remain in page memory unless explicitly saved or exported. Browser localStorage key `ghosttrack.atlas.v1` stores the language preference, manually saved snapshots and favorites. Up to 50 snapshots and 50 favorites share an approximately 1.9-million-character budget. This storage is unencrypted and scoped to the exact browser origin, including port. Local and hosted origins have separate saved data.

The privacy page can remove Atlas's browser data after confirmation; downloaded reports, clipboard contents, desktop history and archive records are independent. Export opens a redaction preview; automatic masking does not recognize all personal data. Copy actions copy the original values.

The hosted adapter additionally contacts `data.iana.org` for the official RDAP domain bootstrap and approved registry hosts. It queries only fixed-provider destinations and does not fetch arbitrary user-entered website URLs. It exposes HTTPS/TLS runtime limits instead of claiming a verified certificate. Source queries still reveal the target and connection address to the provider. Hosting infrastructure may process operational request metadata under its own policies; this application adds no analytics or query database.

An update check contacts the repository's public GitHub releases API only after the user requests it. Snapshot imports are parsed as bounded data, not executed. Full behavior is documented in the [Atlas guide](atlas.md).

### Classic desktop settings, history and archive

The default directory is `%LOCALAPPDATA%\GhostTrackDesk`. You can override it with `GHOSTTRACK_DATA_DIR`.

| Data | Location and retention | Removal |
| --- | --- | --- |
| Preferences | `state.json`: language, default phone region, and history-persistence choice | Change the setting or remove the file while the app is closed |
| Query history | Session memory by default; up to 50 entries. If enabled, `state.json` also stores inputs, tool/region/platform context, times, and result fields, within an approximately 1.9 MB saved-state limit | **Clear history** clears session and persisted history |
| Authorized account archive | `archive.json`: up to 200 records containing phone numbers, normalized profile URLs, platform, user-declared source, optional note, and save time | Delete records in **Manage archive**, or remove the file while the app is closed |
| Error log | `application.log`, with a 200,000-byte rotation threshold and one backup; query/callback errors log exception type names | Close the app and remove the log and its backup |
| Exported reports | The destination you choose; may contain full inputs and result fields | Delete the report through your filesystem or storage provider |

Clearing query history does **not** delete archive records or exported files. Archive persistence is independent of the history setting. Exported archive reports contain the associations you saved and require the same care as the local archive.

The application writes state and archive files as JSON. It uses temporary files and atomic replacement with bounded retries for temporary Windows access denials. Those files are not encrypted by GhostTrack. Anyone with access to your account, selected data directory, backups, or exported files may be able to read them. Choose an appropriate directory and remove records you no longer need.

## Android local data and permissions

Android stores the language and selected tool in application-private SharedPreferences. It has no app-managed persistent query-history file and does not include the Windows account archive.

The current input and result live in memory. Android may preserve input, region/platform selection, and a response smaller than 200,000 characters in the Activity's saved state to restore an interrupted screen. This is separate from a browsable query history; do not rely on it as a saved report. The manifest disables Android application backup.

The manifest declares **Internet** access and does not request location, contacts, SMS, phone, or broad storage permissions. The user-initiated **Paste** control reads clipboard text; copying a result places it on the system clipboard. Android's document picker grants access to the report destination you select, which may belong to a cloud-backed document provider. That provider's storage behavior then applies to the exported file.

Uninstalling or clearing app data removes application preferences through Android's normal controls. Files you exported and text you copied remain under the relevant document provider or clipboard controls.

## Public share parameters and clipboard contents

Xiaohongshu profile links can require public `xsec_token` and `xsec_source` parameters. The normalizer keeps these supported parameters; history, archive records, copied values, and reports can therefore include them. Remove sensitive context before posting a report, screenshot, or issue.

Copy and export are explicit user actions. The application does not clear your system clipboard after you copy a value. Other applications or clipboard managers may retain copied text according to their own settings.

## Query safeguards and limits

- **Website targets:** accept HTTPS on port 443 without embedded credentials or fragments. Resolve and validate public addresses, reject mixed public/private answers, connect to a validated address, and retain the original hostname for TLS verification. Each redirect goes through validation again.
- **Bounded content:** the website client permits at most four requests and limits response reads and gzip/deflate output to 128 KiB. Public JSON requests limit the response to 1 MiB; profile metadata reads stop at 512 KiB. The clients use timeouts and cancellation checks.
- **Limited output:** RDAP reports omit registrant contact records. GitHub reports read public profile/repository fields and do not request an account's email data. Platform profile queries extract public title/description metadata without executing JavaScript or importing login cookies.
- **Conservative status:** a restricted page, failed request, or missing field does not verify account absence. Domain overview preserves independent source statuses and partial results.
- **Local archive declarations:** the user supplies an association and declares its permitted source. The program checks phone format and platform URL structure; it does not verify consent, identity, or association accuracy online.
- **Reports:** HTML output escapes field values; CSV prefixes formula-like values to reduce unintended spreadsheet execution.
- **Cancellation:** the interface ignores late results from cancelled queries. It cannot retract a request a provider has already received.

These measures constrain the implemented queries; they do not establish the accuracy of third-party data. IP and phone metadata do not reveal a device's live position. Generated username URLs and saved archive associations do not prove identity or ownership.

## Developer signing material

Android release builds create a private keystore and credential file under `%LOCALAPPDATA%\GhostTrackBuild` on Windows, or `~/.local/share/GhostTrackBuild` elsewhere. The build script restricts filesystem access and keeps these files outside the checkout. Back up that directory securely; do not upload it, its passwords, or its private key. Published signature summaries contain public certificate information only.

For a suspected vulnerability, follow [SECURITY.md](../SECURITY.md). For ordinary defects, use the [issue templates](https://github.com/Serennity007/GhostTrack/issues/new/choose) and remove personal query data from examples.
