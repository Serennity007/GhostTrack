# Support

## Find the right place

| Need | Where to go |
|---|---|
| Install or use the Windows application | [Windows guide](docs/windows.md) |
| Install, use or build the Android application | [Android guide](docs/android.md) |
| Understand tools, fields and platform differences | [Feature guide](docs/FEATURES.md) |
| Understand network access and local storage | [Privacy guide](docs/PRIVACY.md) |
| Report a reproducible problem | [Bug report](https://github.com/Serennity007/GhostTrack/issues/new?template=bug_report.yml) |
| Propose a feature or public-data source | [Feature request](https://github.com/Serennity007/GhostTrack/issues/new?template=feature_request.yml) |
| Report a suspected vulnerability | [Private security report](https://github.com/Serennity007/GhostTrack/security/advisories/new) and [security policy](SECURITY.md) |

Search [existing issues](https://github.com/Serennity007/GhostTrack/issues) before opening a new one. English is the primary repository language. Clear reports in another language are welcome; include exact error messages so they can be matched to the source code.

## Make a useful report

Include the application version, operating system version, selected module and interface language, the steps you followed, what you expected and what happened. Where possible, reproduce with a public example such as `python.org`, `8.8.8.8` or `octocat`. Describe whether the problem happens consistently or only on one network.

For a UI problem, attach a screenshot showing the relevant controls and note the display scaling or Android device configuration. For exports, state the chosen format and the operation that failed. Distinguish a source checkout from an official release package.

Before attaching anything, remove access tokens, private URLs, real phone numbers, personal history, local archive contents, signing material and unrelated desktop content. Do not upload an entire settings directory. Report query inputs only when they are safe to publish.

## Common limitations

- Public services can rate-limit, change their pages, require login or return incomplete data. Include the source status in your report; missing fields alone do not establish an application bug.
- Phone-number regions and IP database locations are metadata, not live device locations.
- Generated username links do not verify that an account exists or belongs to a person.
- The Windows authorized account archive stores user-supplied associations locally; it does not discover private accounts from phone numbers.
- Windows and Android do not always share the same release version or module count. Check the [feature comparison](docs/FEATURES.md) before reporting a missing platform feature.

Repository support is handled through issues. There is no guaranteed response time or dedicated private support service.
