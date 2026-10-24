# Validation · Windows / Atlas 1.9.0

Checks performed on 24 October 2026. These results describe the tested build and environment; third-party data and availability can change.

| Check | Result |
| --- | --- |
| Python regression suite | 91 tests passed, including desktop lifecycle, packaged-source isolation, public-query parsing, loopback boundaries, cancellation and release packaging |
| JavaScript regression suite | 13 tests passed: evidence interpretation, failed-source comparison, TTL/order noise, redaction, safe reports, hosted destinations and runtime limits |
| Packaged Windows application | Built with Python 3.11 / PyInstaller for Windows x64; Atlas entry launches the owned loopback service |
| Packaged local engine | Reserved phone example normalized offline; python.org RDAP, DNS and verified HTTPS/TLS returned successfully |
| Public hosted deployment | Anonymous HTTP 200 page and a real example.com query verified; RDAP and DNS available; unsupported HTTPS correctly marked limited |
| Browser workflows | Real query, explicit snapshot save and refresh recovery, favorites, two-snapshot comparison, deduplicated two-domain queue, pause/resume, copy and export exercised |
| Reports | JSON, CSV and HTML downloads verified; redaction preview retains observation time and masks targets/IPs/recognized phone formats/URL parameters; source fields and derived observations remain distinct |
| Interface | Chinese, English, Japanese and Spanish controls inspected; 1280-pixel desktop and 390-pixel mobile layouts checked without document overflow |
| Documentation | Relative links, images and heading anchors checked; bundled manuals and policies included with the executable |

The hosted adapter has seven tools. It intentionally does not connect directly to arbitrary websites or inspect raw TLS certificates; the local engine supplies those capabilities. Android's native 1.6.0 package was not rebuilt for this release. An emulator/desktop browser check does not establish behavior on every physical device.

Local and hosted queries use public examples. Validation outputs are stored in the ignored build directory; no personal account archive, signing secret, API token or private query history is published.
