# Feature catalogue

[Project home](../README.md) · [Windows guide](windows.md) · [Android guide](android.md) · [Privacy and data flow](PRIVACY.md)

GhostTrack organizes public resource lookups into structured results with query context and report export. The published Windows **1.8.0** edition has **12 tools**; Android **1.6.0** has **11**. The local authorized account archive is Windows-only.

## Platform support

| Capability | Windows 1.8.0 | Android 1.6.0 |
| --- | --- | --- |
| Public-data tools listed below | 11 | 11 |
| Local authorized account archive | Yes, tool 12 | No |
| Interface languages | English, Simplified Chinese, Japanese, Spanish | English, Simplified Chinese, Japanese, Spanish |
| Example input and clipboard paste | Yes | Yes, touch controls |
| Field/value filtering and complete-value reading | Table and detail pane | Selectable result cards |
| Single-value and complete-result copy | Buttons, double-click, Ctrl+C | Per-field and Copy all buttons |
| JSON, CSV, and HTML reports | Native save dialog | Android document picker |
| Background query cancellation | Yes | Yes |
| Query history | Session history, optional local persistence | No app-managed history |
| Saved preferences | Language, phone region, history choice | Language and selected tool |

Repository documentation also includes French. The application interface currently offers the four languages in the table.

## Public-data tools

| Tool | Input | Result and limits |
| --- | --- | --- |
| **Domain overview** | A domain such as `python.org` | RDAP registration, eight DNS record types, and HTTPS/TLS in parallel. Results retain their source namespaces and independent status; a failed source does not discard the others. The Windows view shows actual source completion progress. |
| **Domain registration** | A registered domain such as `example.com` | RDAP status, registrar when available, name servers, DNSSEC delegation flag, and available registration/expiration/update dates. The report excludes registrant contact records. A subdomain usually has no separate registration. |
| **DNS records** | A domain such as `example.com` | A, AAAA, CNAME, MX, NS, TXT, SOA, and CAA through Google Public DNS. Records include TTL. Limit: 20 answers and 6,000 characters per type; truncation appears in the report. Empty answers, `NXDOMAIN`, and request errors appear separately. |
| **Website and certificate** | A public HTTPS URL or domain, for example `https://www.python.org/` | HTTP status, connected address, page title, content encoding/status, selected response headers, redirect chain, elapsed time, certificate issuer, validity dates, remaining days, and covered DNS names. Uses public port 443, strict TLS checks, at most four requests, and bounded content reads/decompression. It does not execute page JavaScript. |
| **IP / ASN registration** | Public IPv4/IPv6 or `AS15169` | RDAP network name/handle, address range, calculated CIDR when available, registration country code, dates, or ASN range. Network registration does not identify an individual using an address. |
| **IP location** | Public IPv4/IPv6 such as `8.8.8.8` | Provider database country, region, city, estimated coordinates, ISP, organization, ASN, network domain, postal metadata, and time zone when available. These are database estimates, not live device locations. |
| **My public IP** | No target | The public IP address that the external IP service sees for your request. A VPN, proxy, mobile gateway, or NAT can affect this value. |
| **Phone metadata** | `+12025550123`, or a national number and region code | Offline number formatting, calling code, region description, carrier metadata, time zones, validity, and possibility checks from the bundled `phonenumbers` database. No subscriber identity or live location. |
| **Username links** | A username without spaces, up to 100 characters | Generated GitHub, Instagram, and X profile URLs. The tool does not request these pages, check account existence, or establish ownership. |
| **GitHub public profile** | `octocat` or `https://github.com/octocat` | Public login/name/bio/type, repository/follower/following counts, account dates, and five public repositories sorted by update time. Anonymous API limits can leave repository details unavailable while retaining profile fields. |
| **Chinese public profiles** | A supported profile URL, identifier, or one-link share message | Normalized profile URL, HTTP/access status, and readable public title/description. Supports the seven platforms below; it does not search private APIs or bypass login/CAPTCHA. |

Use a two-letter region such as `US`, `CN`, or `JP` for national phone numbers. International `+` format avoids ambiguity. A phone validation result describes the numbering plan; it does not confirm that someone currently uses the number.

## Seven Chinese platforms

| Platform | Supported input | Important distinction |
| --- | --- | --- |
| **Douyin** | `https://www.douyin.com/user/…`, its URL user identifier, supported `v.douyin.com` profile share link | A displayed Douyin handle is not the URL user identifier. |
| **Xiaohongshu** | `https://www.xiaohongshu.com/user/profile/…`, 24-character hexadecimal user ID, supported `xhslink.com` profile share link | Profile shares may need their `xsec_token` and `xsec_source` parameters. |
| **Kuaishou** | `https://www.kuaishou.com/profile/…` or profile identifier | Use an identifier rather than a display nickname. |
| **Bilibili** | Numeric UID or `https://space.bilibili.com/…` | A UID differs from a nickname. |
| **Weibo** | Numeric UID or `https://weibo.com/u/…` | Login redirects can limit the public response. |
| **Zhihu** | `https://www.zhihu.com/people/…` or URL identifier | A URL identifier differs from a display name. |
| **Douban** | `https://www.douban.com/people/…` or URL identifier | A URL identifier differs from a display name. |

**Auto** recognizes a supported full URL. Choose the platform yourself for a bare identifier. A share message may contain one URL; multiple URLs are rejected. Videos, posts, and Xiaohongshu notes are not profile inputs.

The short-link resolver permits the selected platform's listed official short-link/profile hosts and at most four requests. It rejects unrelated hosts and login/verification routes. Short links that expire or require scripts need a fresh full profile URL from your browser.

Public metadata depends on the platform's response. The tool does not promise follower counts, post collections, private contact details, or real-name identity. A login page, generic landing page, 403/412/429 response, or missing metadata establishes a limit on this query, not whether the account exists.

## Windows authorized account archive

Tool 12 searches records you saved on your own computer. From a Chinese platform result, save a known phone/profile association and declare its source:

- Your own authorized phone and profile information.
- A number the profile owner published on that public profile.

The application records your declaration, optional note, and UTC save time. It normalizes a valid phone to E.164 and the profile URL to the selected platform. Saving an existing phone/platform/profile combination updates the record; the archive holds up to 200 records.

Search by keyword or a phone fragment of at least three digits. The query view displays up to 12 matches; Manage archive shows the stored list, deletes selected records, and exports all records as JSON, CSV, or HTML. Archive records persist separately from history.

The archive does not verify consent, call a service to validate associations, or discover accounts from a phone number. It only records associations the user supplies under the two declared sources.

## Working with results

- **Context:** reports retain the selected tool, query input, and UTC timestamp. Source links and per-source status appear where the service supplies them.
- **Filtering:** match field names or values without removing the complete result. Copy all and export include the fields hidden by a filter.
- **Readable values:** select a Windows row to read its full value in the detail pane; Android supports selectable text inside result cards.
- **Reports:** JSON preserves fields, CSV uses UTF-8 with a BOM and formula-text protection, and HTML opens offline with escaped values.
- **Cancellation:** cancelled and stale responses cannot replace a newer result. An already running network read may finish only when its timeout expires.
- **History:** Windows keeps up to 50 session queries and can save them locally on opt-in. Switching tools clears the current view without deleting completed history. Android has no app-managed query history.

Inspect the query timestamp, source, input, and status before drawing conclusions. A partial report can contain useful source data alongside an error. A blank field, access restriction, or generated URL is not identity verification.

For installation, examples, keyboard shortcuts, and development commands, use the [Windows guide](windows.md) or [Android guide](android.md). See [Privacy and data flow](PRIVACY.md) for the exact providers and local storage behavior.
