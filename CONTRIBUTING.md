# Contributing to GhostTrack Console

Contributions that make public-data queries more reliable, results easier to verify, or the Windows and Android interfaces clearer are welcome. The repository's primary language is English; use English for new documentation, issue titles and pull request descriptions. Keep the existing translated guides and four-language application strings in sync when behavior changes.

## Before you start

- Search [existing issues](https://github.com/Serennity007/GhostTrack/issues) before opening a new one. Describe substantial new modules in a feature request first, including their public source and expected fields.
- Use the [private security reporting channel](https://github.com/Serennity007/GhostTrack/security/advisories/new) for suspected vulnerabilities; see [SECURITY.md](SECURITY.md).
- Use synthetic inputs, your own resources, or public documentation examples in tests, screenshots and reports. Remove tokens, personal history, phone numbers and private links before sharing.

## Run the Windows application from source

Use Windows x64 and Python 3.11 with Tkinter installed. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
```

The complete test suite exercises Tkinter windows and needs a working desktop session. Most provider tests use mocked responses rather than live services. Check changed network behavior separately against a public example when appropriate; record provider errors or rate limits honestly.

For an isolated manual session, keep test settings and archives separate from your usual application data:

```powershell
$env:GHOSTTRACK_DATA_DIR = Join-Path $PWD 'build\manual-review'
.\.venv\Scripts\python.exe desktop.py
```

To build the portable Windows package:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe build_windows.py
```

For Android prerequisites, the Gradle wrapper, signing and packaging, follow the [Android guide](docs/android.md). Keep signing keys and credentials outside the repository. Do not submit generated APKs, ZIPs, virtual environments or local build directories in a pull request.

## Where changes belong

| Area | Files |
|---|---|
| Query dispatch and public providers | `queries.py`, `public_data.py`, `platforms.py` |
| Windows interface and persistence | `desktop.py`, `storage.py`, `archive.py` |
| Application translations and exports | `i18n.py`, `reports.py` |
| Android interface and JSON boundary | `android/app/src/main/java/`, `android/app/src/main/python/mobile_bridge.py` |
| Regression coverage | Root-level `test_*.py` files |

Shared query code should remain independent of Tkinter and Android UI classes. Verify that a new import is also available in the Android generated Python source set; desktop-only tests can otherwise hide packaging failures.

## Query and UI expectations

- Preserve source URLs, query timestamps and partial results. Distinguish missing data, blocked access, failed requests and verified results.
- Bound request timeouts, response sizes, redirects and parallel work. Preserve public-address checks and TLS certificate validation.
- Use public, unauthenticated sources. Do not add login or CAPTCHA bypasses, private-account discovery, or phone-to-account identification. The local authorized archive only stores associations explicitly supplied by the user.
- Add meaningful regression coverage for changed behavior. For UI changes, check the minimum window size, readable long values, cancellation, copying, export and all four application languages affected by the change.
- Prefer focused patches and existing components. Update the relevant user guide, changelog and screenshots when the visible behavior changes.

## Submit a pull request

Explain the problem, the resulting behavior and how you verified it. Include before/after screenshots for visible UI changes, using public examples without personal information. State which platforms you actually tested and any remaining limitation; do not describe an untested device or build as verified.

Preserve attribution to [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) and the original material in `UPSTREAM_README.md`. Do not invent a license or remove upstream credit.
