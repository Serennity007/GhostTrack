"""Android packaging regressions without a device, SDK or network access."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from build_android import parse_apk_version


ROOT = Path(__file__).resolve().parent


class ApkVersionTests(unittest.TestCase):
    def test_version_comes_from_apk_package_entry(self):
        badging = ("package: name='io.github.serennity.ghosttrack' versionCode='16000' "
                   "versionName='1.6.0' platformBuildVersionName='16'\n"
                   "application-label:'GhostTrack 1.8.0'\n")
        self.assertEqual(parse_apk_version(badging), '1.6.0')
        self.assertEqual(parse_apk_version("package: name='example' versionName='12.34.56'"),
                         '12.34.56')

    def test_missing_ambiguous_and_unsafe_versions_are_rejected(self):
        values = ('', "application-label:'1.6.0'", "package: name='example'",
                  "package: versionName='1.6.0' versionName='1.8.0'",
                  "package: versionName='1.6.0'\npackage: versionName='1.8.0'")
        for value in values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_apk_version(value)
        for version in ('../1.6.0', '1.6.0/other', '1.6.0\\other', '1.6', '1.6.0-beta',
                        '01.6.0', '-1.6.0', '1.6.0\n', '1.6.0"', '1' * 40 + '.0.0'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                parse_apk_version("package: name='example' versionName='" + version + "'")


class PackagedPythonTests(unittest.TestCase):
    def test_declared_shared_sources_import_and_run_without_checkout(self):
        """A host import hid archive.py's absence from the Android source set."""
        gradle = (ROOT / 'android/app/build.gradle').read_text(encoding='utf-8')
        sync = gradle.split("tasks.register('syncSharedPython', Sync)", 1)[1]
        includes = re.search(r'\binclude\s+([^\n]+)', sync).group(1)
        files = re.findall(r"'([^']+\.py)'", includes)
        android_version = re.search(r"\bversionName\s+'([^']+)'", gradle).group(1)
        self.assertTrue(files, 'No Android shared modules were staged')
        with tempfile.TemporaryDirectory(prefix='ghosttrack-packaged-python-') as folder:
            target = Path(folder)
            for name in files:
                shutil.copyfile(ROOT / name, target / name)
            # Model Gradle's generated version.py, never replace a copied desktop version.
            if not (target / 'version.py').exists():
                (target / 'version.py').write_text('VERSION = ' + repr(android_version) + '\n',
                                                 encoding='utf-8')
            shutil.copyfile(ROOT / 'android/app/src/main/python/mobile_bridge.py',
                            target / 'mobile_bridge.py')
            script = ('import json, sys; sys.path.insert(0, ' + repr(str(target)) + '); '
                      'import mobile_bridge as bridge; '
                      'print(json.dumps({"version": json.loads(bridge.bootstrap("en"))["version"], '
                      '"phone": json.loads(bridge.run_query("号码归属地", "+12025550123", '
                      'language="en")), "username": json.loads(bridge.run_query("用户名链接", '
                      '"octocat", language="en"))}))')
            result = subprocess.run([sys.executable, '-I', '-c', script], cwd=target,
                                    capture_output=True, text=True, encoding='utf-8', timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['version'], android_version)
            self.assertTrue(data['phone']['ok'])
            self.assertEqual(data['phone']['raw']['国家呼叫码'], 1)
            self.assertEqual(data['username']['result']['GitHub'], 'https://github.com/octocat')


if __name__ == '__main__':
    unittest.main()
