"""A portable release must contain the manuals linked from its included README."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from build_windows import package_distribution


class WindowsPackagingTests(unittest.TestCase):
    def test_portable_package_includes_atlas_docs_and_matching_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = root / 'dist/v1.9.0/GhostTrack'
            app.mkdir(parents=True)
            (app / 'GhostTrack.exe').write_bytes(b'test executable')
            for name in ('README.md', 'README.zh-CN.md', 'README.en.md', 'README.ja.md', 'README.es.md', 'README.fr.md',
                         'README_WINDOWS.md', 'README_ANDROID.md', 'CHANGELOG.md', 'CHANGELOG.zh-CN.md', 'UPSTREAM_README.md',
                         'CONTRIBUTING.md', 'SECURITY.md', 'SUPPORT.md'):
                (root / name).write_text('[Atlas](docs/atlas.md)', encoding='utf-8')
            (root / 'docs').mkdir()
            (root / 'docs/atlas.md').write_text('Atlas guide', encoding='utf-8')
            archive = package_distribution(root, version='1.9.0')
            with zipfile.ZipFile(archive) as bundle:
                self.assertIn('GhostTrack/GhostTrack.exe', bundle.namelist())
                self.assertIn('GhostTrack/docs/atlas.md', bundle.namelist())
                self.assertIn('GhostTrack/README.md', bundle.namelist())
                self.assertIn('GhostTrack/SECURITY.md', bundle.namelist())
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual((root / 'dist/SHA256SUMS-v1.9.0.txt').read_text().split()[0], digest)


if __name__ == '__main__':
    unittest.main()
