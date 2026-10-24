# Changelog

[English](CHANGELOG.md) · [简体中文](CHANGELOG.zh-CN.md) · [Project home](README.md)

Windows and Android have separate release versions. Entries below identify the platform when a release applies to only one of them.

## 1.9.0 · Windows / Atlas web

- Add Atlas, a browser workbench launched from the Windows application with its own loopback-only public-query service. Preserve the existing 12 desktop tools and archive.
- Add source-backed health observations and field explanations; compare saved snapshots without treating failed sources as deleted data or TTL countdown as a record change.
- Add a paced, deduplicated 50-domain queue with pause/resume/cancel, bounded 429 retries and batch export; add explicit browser-local snapshots and favorites.
- Add redaction previews for targets, IPs, recognized phone formats and URL parameters, with JSON/CSV/HTML export. Add selected-query source status and on-demand release checks.
- Add Chinese, English, Japanese and Spanish browser controls and responsive layouts. Hosted mode supports seven tools; pinned HTTPS/TLS, offline phone metadata and Chinese profiles use the local engine.
- Keep Android's native release at 1.6.0. The source-packaging fixes below remain included in current source.
- Validate 91 Python tests, 13 JavaScript tests, real public-source queries, browser workflows and the packaged Windows engine. [Validation notes](docs/validation-1.9.0.md).

## Repository and Android build maintenance

- Make English the primary repository language. Preserve the Chinese introduction and changelog; add complete English platform guides, a feature catalogue, privacy notes, maintenance instructions, and real English Windows/Android screenshots.
- Add contribution, support, and security policies, bug/feature forms, and a pull request template.
- Fix Android source packaging after the Windows archive addition by including the shared `archive.py` dependency. Generate the mobile Python version from Gradle's Android version rather than the desktop version.
- Name Android artifacts from the built APK's validated version, and add `--output-dir` for verification builds. Add isolated source-packaging and APK-metadata regression tests.
- Verify 78 Python tests and the signed Android release build with Lint. These source changes do not replace the existing Windows 1.8.0 or Android 1.6.0 release assets.

## 1.8.0 · Windows

- Reorganize the 12-tool workbench from 1.7.0 into a query and source pane on the left, with the result table and full-value detail on the right. Retain the authorized account archive.
- Add compact numbered navigation, actual query metrics, and a result toolbar that adapts to the window width.
- Update the Chinese, English, Japanese, Spanish, and French READMEs and the Windows guide. The app interface continues to support Chinese, English, Japanese, and Spanish. This release updates Windows only; the latest Android release remains 1.6.0.

## 1.7.0 · Windows

- Add the authorized account archive as tool 12. Save a phone/profile association from a platform result when it concerns your own authorized information or a number the owner published on their public profile. Record the source and save time; update duplicate phone/platform/profile combinations. Limit the archive to 200 records.
- Search local records by phone digits or keyword, then filter, copy, or export results as JSON, CSV, or HTML. Manage archive can delete selected records or export all records. Archive storage is independent of query history.
- Explain the archive's limits in the save dialog, management view, and four-language help. The archive does not verify associations online or probe platforms for accounts by phone number.
- Use a two-column tool navigation layout so all 12 tools remain visible at the minimum window size. Add 10 archive and interface tests; 75 tests passed for the release.

## 1.6.0 · Windows / Android

- Publish product READMEs in Chinese, English, Japanese, Spanish, and French, with language navigation and Windows/Android download links. The app interface retains its four existing languages.
- Introduce a shared blue-black, mint, and cyan palette. Improve Windows navigation, source sections, metric cards, input focus, and the results area.
- Reduce Android's first-screen heading and spacing; add a compact toolbar, current-tool heading, gradient panels, and touch feedback.
- Include the tested bounded retry for temporary local-file access denials in the Windows package.

## Android 1.5.0

- Add a native Android dark console with Chinese, English, Japanese, and Spanish, 11 query tools, and shared Python services.
- Add touch input, examples, user-initiated paste, query cancellation, result filters, single-value/all-result copy, and JSON/CSV/HTML export through the system document picker.
- Declare only Internet access; request no location, contacts, SMS, or storage permissions. Remember only the language and tool selection.
- Support Android 7.0+ with a signed universal APK for ARM64, ARMv7, and x86_64. Keep the dedicated release key in the build user's data directory.

## Source fix initially absent from existing Windows release packages

- Retry atomic history-file replacement a bounded number of times when Windows reports a temporary access denial. Preserve the old file and report an error if replacement continues to fail.

## 1.5.0

- Add a domain overview that queries RDAP, eight DNS record types, and HTTPS/TLS in parallel. Isolate source failures and show per-source progress, for a total of 11 query tools.
- Add metric cards, source labels, example inputs, panel borders, and clearer navigation. Clear the previous view when switching tools while retaining completed queries in history.
- Fix empty website titles for compressed responses. Add bounded gzip/deflate decoding and explicit content-status fields.
- Add domain overview fields and source-error messages in Chinese, English, Japanese, and Spanish.

## 1.4.0

- Add domain RDAP, eight DNS record types, website response/TLS certificate metadata, IP/ASN registration, and GitHub public profiles, for a total of 10 query tools.
- Expand phone formats and public IP network metadata; show source links and actual query status.
- Add a dark green console, numbered navigation, decorative radar, monospaced striped result rows, actual field counts, and elapsed query time. Retain four-language support.
- Pin public HTTPS connections to validated addresses, enforce TLS checks, bound redirects and response size, and support public resolution for the `198.18.0.0/15` Fake-IP pool.
- Use versioned build output directories so a running older version does not block packaging a new one.

## 1.3.0

- Add Douyin, Xiaohongshu, and Kuaishou public profiles, bringing the supported Chinese platforms to seven.
- Detect profile platforms, extract links from share messages, and expand supported Douyin/Xiaohongshu profile short links through allowed domains. Add detailed input errors and access-status fields.
- Add cancellable background queries, concurrency limits, stale-response isolation, query context, and UTC timestamps.
- Add session history, optional local persistence of up to 50 entries, history review and clearing, and saved language/default-region settings.
- Add result filtering, scrollable full-value details, single-value/all-result copy, clipboard paste, browser opening, and HTML/JSON/CSV reports.
- Add four-language help and settings, a Windows application icon and version resource, DPI handling, and bounded error logs.
- Split service modules, pin dependencies, add automated tests, and provide a Windows build script and CI template. Update the product page and user guide.

## 1.2.0

- Add public profile metadata and access status for Bilibili, Weibo, Zhihu, and Douban.
- Add single-value and full-result copy, double-click/Ctrl+C, and profile opening.
- Fix the small-window layout; include 17 tests.

## 1.1.0

- Add Chinese, English, Japanese, and Spanish, a dark workbench, and structured results.

## 1.0.0

- Add a Chinese Windows GUI, IP and phone queries, username links, and JSON/CSV export.
