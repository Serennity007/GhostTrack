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
                    '--distpath', str(root / 'dist' / f'v{VERSION}'),
                    '--workpath', str(root / 'build' / f'pyinstaller-v{VERSION}'),
                    '--windowed', '--name', 'GhostTrack', '--icon', 'assets/ghosttrack.ico',
                    '--version-file', str(resource), '--add-data', 'assets;assets', '--add-data', 'web;web',
                    '--collect-all', 'phonenumbers', '--copy-metadata', 'phonenumbers',
                    '--copy-metadata', 'requests', 'desktop.py'], cwd=root, check=True)
    package_distribution(root)


def package_distribution(root, version=VERSION):
    """Bundle a built executable with the linked documentation and checksums."""
    root = Path(root)
    distribution = root / 'dist' / f'v{version}' / 'GhostTrack'
    if not (distribution / 'GhostTrack.exe').is_file():
        raise FileNotFoundError('Build the Windows executable before packaging.')
    for filename in ('README.md', 'README.zh-CN.md', 'README.en.md', 'README.ja.md', 'README.es.md', 'README.fr.md',
                     'README_WINDOWS.md', 'README_ANDROID.md', 'CHANGELOG.md', 'CHANGELOG.zh-CN.md', 'UPSTREAM_README.md',
                     'CONTRIBUTING.md', 'SECURITY.md', 'SUPPORT.md'):
        shutil.copy2(root / filename, distribution / filename)
    shutil.copytree(root / 'docs', distribution / 'docs', dirs_exist_ok=True)
    archive = root / 'dist' / f'GhostTrack-v{version}-Windows-x64.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for file in sorted(distribution.rglob('*')):
            if file.is_file():
                bundle.write(file, file.relative_to(distribution.parent))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (root / 'dist' / f'SHA256SUMS-v{version}.txt').write_text(f'{checksum}  {archive.name}\n', encoding='ascii')
    print(f'Built {archive.name} ({archive.stat().st_size:,} bytes)')
    return archive


if __name__ == '__main__':
    main()
