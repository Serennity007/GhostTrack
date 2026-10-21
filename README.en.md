# GhostTrack Console

[简体中文](README.md) · **English** · [日本語](README.ja.md) · [Español](README.es.md) · [Français](README.fr.md)

A public information console for Windows and Android. Twelve Windows tools and eleven Android modules share the same query services, bringing domain records, DNS, website certificates, network registrations and public profiles into a dark interface with source status and exportable results.

> Documentation is available in Chinese, English, Japanese, Spanish and French. The app interface supports four languages: Simplified Chinese, English, Japanese and Spanish.

## Download and install

| Platform | Download v1.7.0 | Installation |
|---|---|---|
| Windows 10/11 x64 | [Portable ZIP](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.7.0/GhostTrack-v1.7.0-Windows-x64.zip) · [Release and SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/windows-v1.7.0) | Extract the entire archive; run `GhostTrack/GhostTrack.exe` |
| Android 7.0+ | [Universal APK](https://github.com/Serennity007/GhostTrack/releases/download/android-v1.6.0/GhostTrack-v1.6.0-Android-universal.apk) · [Release and SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0) | Open the APK in your phone's file manager |

Windows requires no Python installation. Keep the executable with its bundled dependencies. The Android APK includes ARM64, ARMv7 and x86_64; first launch extracts the bundled runtime. Allow installation only for the app you use to open the APK. Use APKs from this repository signed with the same certificate for future updates.

[Windows guide, Chinese](README_WINDOWS.md) · [Android guide and build details, Chinese](README_ANDROID.md) · [Changelog](CHANGELOG.md)

## Interface

![Windows public information console](docs/desktop.png)

<img src="docs/android.png" width="320" alt="Android public information console" />

Numbered navigation, source labels, elapsed time and field counts reflect the current query. Decorative graphics do not indicate that a target is being scanned.

## Twelve query tools

| Tool | Input | Available public information |
|---|---|---|
| Authorized archive | Phone number or keyword | Locally saved consented phone-profile associations, with source and save time |
| Domain overview | Domain | Parallel RDAP, DNS and HTTPS results, with a status for each source |
| Domain records | Domain | Registrar, registration/expiry/update dates, DNSSEC and name servers |
| DNS records | Domain | A, AAAA, CNAME, MX, NS, TXT, SOA, CAA and TTL |
| Website and certificate | Public HTTPS URL | HTTP status, title, redirects, public headers, TLS issuer/validity/SAN |
| IP / ASN registration | Public IP or `AS15169` | Registered ranges, CIDR, network names, country codes and dates |
| GitHub public profile | Username or profile URL | Public biography, counts, creation date and five recent public repositories |
| Chinese platform profiles | Profile URL, share text or platform user ID | Readable title, description, access status, source and query time |
| IP location | Public IPv4 / IPv6 | Estimated database location, network organization, provider, ASN and time zone |
| My public IP | No input | Your current network's public egress IP |
| Phone metadata | Number and default region | Locally parsed numbering region, carrier, time zones, formats and validity |
| Username links | Username | Generates GitHub, Instagram and X profile links without verifying account existence |

Supported platforms: **Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu and Douban**. Prefer complete profile URLs. Some Douyin and Xiaohongshu profile share links can be expanded. Display names, Douyin handles, video links and note links are not substitutes for the required profile identifier.

## Working with results

- Fill an example without sending a request; cancel queries and ignore late responses.
- Filter fields and values, inspect full text, copy one value or all results, and open the source.
- Export JSON, UTF-8 BOM CSV or standalone HTML, including the tool, input and UTC time. CSV protects formula-like text.
- Windows: double-click / Ctrl+C to copy, Enter to query, Esc to cancel. Android: touch controls and the system document picker for export.
- Windows keeps up to 50 session history entries. Saving history across sessions is optional and off by default. Android does not persist query history; it remembers the language and selected tool.
- "Save to archive" stores a platform result's profile with a phone number you own or that the owner published (with source and save time). The sidebar Archive dialog deletes and exports records; tool 12 searches this local archive by number or keyword.

## Sources, privacy and limits

Queries use [RDAP](https://about.rdap.org/), [Google Public DNS](https://developers.google.com/speed/public-dns/docs/doh/json), the [GitHub public API](https://docs.github.com/en/rest/users/users#get-a-user), ipwho.is, api.ipify.org and the public websites or profiles you enter. Network queries send their target to the relevant service. Phone metadata is parsed locally. There is no project relay server, account login or analytics telemetry.

Login requirements, CAPTCHAs, JavaScript, rate limits and outages can limit results. The app preserves available data and source status; it does not bypass access controls or treat HTTP 200 as verified identity. Website queries accept public HTTPS on port 443, validate certificates and bound redirects and response size. Missing values are not invented. RDAP exports exclude registrant contact details.

**Phone numbering regions and IP database locations are not live device locations. There is no reverse phone lookup for private platform accounts, real-name identification or cross-platform identity matching; the authorized archive only stores associations you explicitly save with a declared source, stays on this device and can be deleted anytime.** Query only public information you are entitled to access and follow each service's terms.

Windows settings and optional history live in `%LOCALAPPDATA%\GhostTrackDesk`; history can be cleared in the app. Error logs omit query content. Android requests Internet permission only, without location, contacts, SMS, phone or broad storage access. Manage exported files, clipboard contents and shared URLs with care because they may contain query data.

## Develop and build

Python 3.11 x64; Windows example:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

Android needs JDK 17 and Android SDK Platform 36 / Build Tools 36.0.0. A Gradle Wrapper is included:

```powershell
$env:JAVA_HOME = 'path to JDK 17'
$env:ANDROID_HOME = 'path to Android SDK'
.\.venv\Scripts\python.exe build_android.py --gradle .\android\gradlew.bat
```

Build scripts run tests and produce release files and SHA256 checksums; the Android script also runs Lint and verifies the APK signature. Keep signing keys outside Git and back them up as described in the [Android guide](README_ANDROID.md). The [Windows workflow example](docs/windows-workflow.example.yml) is a template, not a claim that hosted CI is enabled.

## Credits and feedback

Extended from [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack). The original `GhostTR.py` entry point and [upstream README](UPSTREAM_README.md) are retained. This project is not an official client of the queried platforms.

For [issues](https://github.com/Serennity007/GhostTrack/issues), include your OS, app version and reproduction steps. Do not attach tokens, private keys, personal query history or private links.
