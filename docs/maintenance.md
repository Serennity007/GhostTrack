# Repository and release maintenance

[Project home](../README.md) · [Contributing](../CONTRIBUTING.md) · [Changelog](../CHANGELOG.md)

Use this checklist when changing a feature or publishing a package. Windows and Android are versioned separately; a desktop release does not imply a mobile release with the same features.

## Feature changes

- Update the [feature catalogue](FEATURES.md), platform matrix, input examples, and source limitations when behavior changes.
- Add focused regression coverage for query, parsing, storage, or packaging changes. Run `python -m unittest discover -v`.
- Check the relevant real interface in English, Chinese, Japanese, and Spanish. Review long labels, copy actions, cancellation, partial failures, and export.
- Update the [Windows](windows.md) or [Android](android.md) guide and the English changelog. Keep localized introductions consistent with platform availability.
- Use public examples in screenshots. Replace images only after checking them against the running application.

## Windows package

1. Set the desktop version in `version.py` and update the Windows changelog entry.
2. Run `python build_windows.py` with the documented build dependencies installed.
3. Start the packaged EXE from the extracted archive using a separate `GHOSTTRACK_DATA_DIR`. Check a public network query, an offline phone example, copy, and JSON/CSV/HTML export.
4. Verify the archive checksum. Publish the ZIP and its SHA256 file under `windows-v<version>` with the required OS and known limits.

## Android package

1. Set `versionName` and a monotonically increasing `versionCode` in `android/app/build.gradle`. The generated shared Python version follows this Android version.
2. Restore the existing signing backup outside the repository. Never commit credentials or replace the signing key for an update.
3. Run `python build_android.py --gradle .\android\gradlew.bat`. For verification builds, use `--output-dir build/android-package-validation` to preserve published local assets.
4. Check tests, Android Lint, APK signature verification, and the actual APK version. The output filename is derived from the built APK.
5. Test installation or upgrade, launch, a public domain query, offline phone metadata, cancellation, and document-picker export. An emulator check does not cover every physical device or ABI.
6. Publish the APK, SHA256 file, and certificate verification report under `android-v<version>`.

## Publish and verify

- State the changes for the platform being released, validation performed, and any known limitations.
- Confirm that download links, version labels, feature availability, and screenshot captions match the published assets.
- Verify the repository's English About text, release homepage, issue forms, and private security reporting route.
- Check links in Markdown and issue templates before pushing. Keep the upstream attribution and dependency license notices intact.

The workflow in `windows-workflow.example.yml` is an example only. Builds described here do not imply that GitHub Actions runs automatically.
