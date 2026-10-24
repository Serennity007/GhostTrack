# Security policy

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/Serennity007/GhostTrack/security/advisories/new) for suspected vulnerabilities in GhostTrack Console. Do not publish exploit details, credentials or personal query results in a public issue.

Include:

- The affected application version, platform and component.
- A description of the impact and any prerequisites.
- Minimal reproduction steps using synthetic data or resources you control.
- Relevant redacted logs, screenshots or a small proof of concept.
- A proposed fix, if you have one.

Do not include signing keys, access tokens, personal archives or unrelated third-party data. A report does not require probing other people's accounts or systems.

## Scope

Useful reports include unintended access to private network addresses, TLS validation bypasses, unsafe redirect handling, code execution, report injection, credential exposure, or unintended disclosure of locally stored data.

Inaccurate public-provider data, missing profile fields, access restrictions and ordinary UI bugs belong in [Issues](https://github.com/Serennity007/GhostTrack/issues), unless they demonstrate a security impact. Vulnerabilities in a queried platform should be reported to that platform rather than this repository.

## Releases and updates

Start by checking the latest release for the affected platform: [Windows v1.9.0](https://github.com/Serennity007/GhostTrack/releases/tag/windows-v1.9.0) or [Android v1.6.0](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0). The platform version numbers can differ. Older packages remain historical downloads; there is no separate maintenance commitment for every past release.

Download packages and SHA256 files from this repository's [Releases](https://github.com/Serennity007/GhostTrack/releases). Android updates must use the project's existing release signing certificate. A checksum verifies that a file matches the published asset; it does not replace checking the download source.

## Data handling

Network queries contact their public providers directly. Phone-number metadata is parsed locally. Optional Windows history and the authorized account archive are local files; exported reports and copied text can contain the input and returned data. See the [privacy guide](docs/PRIVACY.md) for storage and source details.
