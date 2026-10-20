"""Run tests, build the portable Windows app, and generate ZIP + SHA256 assets."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys
import zipfile

from tools.build_assets import build_icon
from version import VERSION


def main():
    if sys.platform != 'win32':
        raise SystemExit('Build this Windows application on Windows x64 with Python 3.11.')
    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-v'], cwd=root, check=True)
    build_icon(root / 'assets' / 'ghosttrack.ico')
    resource = root / 'build' / 'resources' / 'version.txt'
    resource.parent.mkdir(parents=True, exist_ok=True)
    numbers = tuple(map(int, VERSION.split('.'))) + (0,)
    resource.write_text(f'''VSVersionInfo(
ffi=FixedFileInfo(filevers={numbers!r}, prodvers={numbers!r}, mask=0x3f, flags=0,
OS=0x40004, fileType=0x1, subtype=0x0, date=(0,0)),
kids=[StringFileInfo([StringTable('040904B0', [
StringStruct('FileDescription','GhostTrack Desktop'),
StringStruct('FileVersion','{VERSION}'),
StringStruct('ProductName','GhostTrack Desktop'),
StringStruct('ProductVersion','{VERSION}'),
StringStruct('OriginalFilename','GhostTrack.exe'),
StringStruct('Comments','Based on HunxByts/GhostTrack')])]),
VarFileInfo([VarStruct('Translation',[1033,1200])])])''', encoding='utf-8')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
                    '--windowed', '--name', 'GhostTrack', '--icon', 'assets/ghosttrack.ico',
                    '--version-file', str(resource), '--add-data', 'assets;assets',
                    '--collect-all', 'phonenumbers', '--copy-metadata', 'phonenumbers',
                    '--copy-metadata', 'requests', 'desktop.py'], cwd=root, check=True)
    distribution = root / 'dist' / 'GhostTrack'
    for filename in ('README_WINDOWS.md', 'CHANGELOG.md', 'UPSTREAM_README.md'):
        shutil.copy2(root / filename, distribution / filename)
    archive = root / 'dist' / f'GhostTrack-v{VERSION}-Windows-x64.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for file in sorted(distribution.rglob('*')):
            if file.is_file():
                bundle.write(file, file.relative_to(distribution.parent))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (root / 'dist' / f'SHA256SUMS-v{VERSION}.txt').write_text(f'{checksum}  {archive.name}\n', encoding='ascii')
    print(f'Built {archive.name} ({archive.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
