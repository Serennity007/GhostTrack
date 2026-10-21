# Android guide

[English home](../README.md) · [中文使用说明](../README_ANDROID.md) · [Windows guide](windows.md) · [Changelog](../CHANGELOG.md)

GhostTrack for Android uses a native touch interface and shares the public-data query services with the Windows edition. The current published Android release is **1.6.0**, with 11 tools. It supports English, Simplified Chinese, Japanese, and Spanish. The Windows-only authorized account archive is not part of the Android interface.

<img src="screenshots/android-overview-en.png" width="300" alt="GhostTrack Android query workbench in English" /> <img src="screenshots/android-results-en.png" width="300" alt="GhostTrack Android results in English" />

## Install and update

1. Download [GhostTrack-v1.6.0-Android-universal.apk](https://github.com/Serennity007/GhostTrack/releases/download/android-v1.6.0/GhostTrack-v1.6.0-Android-universal.apk) from this repository's [Android release](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0).
2. Open the APK in your phone's file manager. If Android requests permission to install from that source, grant it to the application you used to open the APK.
3. Open GhostTrack. The first launch extracts its bundled Python runtime and may take longer than subsequent launches.

Use **Android 7.0 or later**. The universal APK includes ARM64, ARMv7, and x86_64. The project signs release APKs with its own release certificate; these packages do not come from Google Play. To update an existing installation, use a release from the same repository signed with the same certificate.

## First query

Select English in the language picker. Choose **Domain overview**, enter `python.org`, then tap **Query**. You receive a combined RDAP, DNS, and HTTPS/TLS report; partial source failures retain the available results. The cards show the result fields and elapsed time.

Tap **Example** to fill the current tool's sample without making a request. **Paste** reads the clipboard when you request it. Select a platform for a bare profile ID, or use **Auto** with a supported full profile URL.

## Tools

| Tool | Example input | Output |
| --- | --- | --- |
| Domain overview | `python.org` | RDAP, DNS, and website/TLS information with source status |
| Domain registration | `example.com` | Public RDAP registration metadata and dates |
| DNS records | `example.com` | A, AAAA, CNAME, MX, NS, TXT, SOA, and CAA records, including TTL |
| Website and certificate | `https://www.python.org/` | Response, page title, redirect chain, selected headers, and certificate metadata |
| IP / ASN registration | `8.8.8.8` or `AS15169` | Public network registration and address ranges |
| IP location | `8.8.8.8` | Database estimates for region, ISP, organization, ASN, and time zone |
| My public IP | No input | Public address visible to the service |
| Phone metadata | `+12025550123` | Number formats, validity, region, carrier metadata, and time zones |
| Username links | `octocat` | Candidate GitHub, Instagram, and X profile links |
| GitHub public profile | `octocat` or its GitHub profile URL | Public profile fields and counts, plus five recent public repositories |
| Chinese platforms | `https://space.bilibili.com/2` | Profile URL, readable page metadata, and access status |

Phone metadata uses the bundled database and works offline. For a national number, enter a two-letter phone region such as `US`, `CN`, or `JP`; an international `+` number avoids ambiguity. Phone regions and IP database locations describe metadata rather than a device's live position. Username links do not confirm that an account exists or belongs to a person.

## Public profiles and share links

The profile tool supports Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu, and Douban. Use a profile URL, the platform's supported user identifier, or a share message containing one profile link. It does not search display nicknames.

- Douyin uses `/user/…`; a displayed Douyin handle is a different identifier.
- Xiaohongshu uses `/user/profile/…` or a 24-character hexadecimal user ID. Keep required public share parameters.
- Kuaishou uses `/profile/…`.
- Bilibili uses a numeric UID or `space.bilibili.com/…`; Weibo uses a numeric UID or `weibo.com/u/…`.
- Zhihu and Douban use their `/people/…` URL identifiers.

Supported Douyin and Xiaohongshu profile short links expand only through listed official platform hosts, with a four-request limit. Video and post links are not profile inputs. For an expired or scripted share link, open it in your browser and copy the final profile URL. See the [full input table](windows.md#chinese-public-profiles).

The query reads public HTML titles and descriptions. Login, CAPTCHA, JavaScript requirements, HTTP restrictions, and rate limits can reduce the available information. A restricted response does not establish that the account is absent. The application does not identify private accounts from phone numbers.

## Results, cancellation, and reports

Filter results by field or value, tap a field's **Copy** button, or use **Copy all** for the complete result. Copy all and export include fields hidden by the current filter. You can also select text within a value.

Tap **Cancel** to stop accepting the current result. A network read can continue until its timeout, but a late response from that request will not replace a newer query.

Tap **Export**, choose JSON, CSV, or HTML, then choose a destination in Android's document picker. The app does not need broad storage access. Reports include the query tool, input, and UTC timestamp. CSV uses UTF-8 with a BOM and formula-text protection; HTML opens offline. If Android interrupts an export, return to the result and export it again.

## Permissions and local data

The app declares the **Internet** permission. It does not request location, contacts, SMS, phone, or broad storage permissions. Queries contact the public providers directly; the project does not operate a query relay server or require service credentials. Third-party providers receive the target you query.

Android remembers the language and selected tool. It has no app-managed query history and does not provide the desktop archive. Android may preserve the current input and a bounded result in Activity saved state to restore an interrupted screen; the result can still disappear when you close the app or Android reclaims the process. Export results you want to keep. Android application backup is disabled in the manifest. See [Privacy and data flow](PRIVACY.md) for details.

The shared website client accepts public HTTPS targets on port 443, validates TLS and resolved addresses, limits redirects and response size, and bounds decompression. Private or loopback targets are rejected. Provider limits and proxy-only networks may affect results; see [network troubleshooting](windows.md#network-limits-and-troubleshooting).

## Troubleshooting

- **Installation fails:** confirm Android 7.0+ and a supported ABI, then download the complete APK from the release page.
- **Update reports a signing conflict:** check that both packages come from this repository. A build made with your own new key cannot update the project's published APK in place.
- **First start takes time:** allow the bundled runtime to initialize before starting a query.
- **No matching public profile data:** check the profile URL and source status. Try opening the profile in your own browser.
- **No destination picker or interrupted export:** choose Export again after returning to the application. Check that your device has a document provider.
- **A result disappears after reopening:** Android does not save query history. Use a report file for records you need later.

For a [bug report](https://github.com/Serennity007/GhostTrack/issues/new/choose), include your app version, Android version, device/ABI, and reproduction steps. Remove personal results and private URLs from screenshots or logs.

## Build from source

Use the toolchain pinned by the project:

| Component | Version |
| --- | --- |
| JDK | 17 |
| Gradle | 8.13 |
| Android SDK Platform | 36 |
| Android Build Tools | 36.0.0 |
| Android Gradle Plugin | 8.13.2 |
| Chaquopy | 17.1.0 |
| Python | 3.11 |

Install the Android SDK components and provide network access to Google Maven, Maven Central, and PyPI. Install Python dependencies into the repository environment, then run from the root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
$env:JAVA_HOME = 'C:\path\to\jdk-17'
$env:ANDROID_HOME = 'C:\path\to\Android\Sdk'
.\.venv\Scripts\python.exe build_android.py --gradle 'C:\path\to\gradle-8.13\bin\gradle.bat'
```

The build script runs Python tests, assembles the release APK, runs Android Lint, verifies the APK signature, and writes the APK, SHA256 checksum, and public certificate summary to `dist/`. Add `--output-dir dist/android-local` to put your own artifacts in a separate directory. The script names artifacts from the APK's actual `versionName`; Windows and Android release versions are independent.

The Gradle `syncSharedPython` task copies shared service modules into a generated directory rather than maintaining a separate Android implementation. It generates Android's `version.py` from Gradle's `versionName`, so the native app, reports, and artifact names use the Android version. No GitHub Actions release workflow is currently enabled.

### Back up your signing key

The first release build creates a keystore and credential file outside the checkout:

- Windows: `%LOCALAPPDATA%\GhostTrackBuild`
- Other platforms: `~/.local/share/GhostTrackBuild`

Back up the **entire signing directory** in a secure location. Losing the key prevents in-place updates to applications signed with it. Do not commit the keystore, credential file, or passwords. The script restricts access to the current Windows user and SYSTEM, or to the current user on other platforms. Your own build key is separate from the key used for this repository's published APKs.

Build requirements follow the [Android Gradle Plugin documentation](https://developer.android.com/build/releases/agp-8-13-0-release-notes) and [Chaquopy Android requirements](https://chaquo.com/chaquopy/doc/current/android.html). See the [contribution guide](../CONTRIBUTING.md) for review and validation expectations. The original project is [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack).
