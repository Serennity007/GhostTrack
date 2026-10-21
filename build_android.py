"""Build, sign and verify the portable Android release without storing secrets in Git."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys

from version import VERSION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gradle', default='gradle.bat' if os.name == 'nt' else 'gradle')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    env = os.environ.copy()
    env['GHOSTTRACK_BUILD_PYTHON'] = sys.executable
    sdk = Path(env.get('ANDROID_HOME', env.get('ANDROID_SDK_ROOT', '')))
    if not (sdk / 'build-tools' / '36.0.0').is_dir():
        raise SystemExit('Set ANDROID_HOME to an SDK with platform 36 and build-tools 36.0.0.')
    java = Path(env['JAVA_HOME']) / 'bin'
    keytool = java / ('keytool.exe' if os.name == 'nt' else 'keytool')
    signing_dir = Path(env.get('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'GhostTrackBuild'
    signing_dir.mkdir(parents=True, exist_ok=True)
    # This directory survives checkout/build cleanup. Back it up securely to preserve update signing.
    if os.name == 'nt':
        account = subprocess.check_output(['whoami'], text=True).strip()
        subprocess.run(['icacls', str(signing_dir), '/inheritance:r', '/grant:r',
                        f'{account}:(OI)(CI)F', 'SYSTEM:(OI)(CI)F'], check=True, capture_output=True)
    credentials = signing_dir / 'android-signing.json'
    keystore = signing_dir / 'ghosttrack-release.p12'
    if not credentials.exists():
        if keystore.exists():
            raise SystemExit('Signing credentials missing for existing key; restore the signing backup.')
        credentials.write_text(json.dumps({'password': secrets.token_urlsafe(40)}), encoding='utf-8')
        if os.name != 'nt':
            credentials.chmod(0o600)
    env['GHOSTTRACK_STORE_PASSWORD'] = json.loads(credentials.read_text(encoding='utf-8'))['password']
    env['GHOSTTRACK_KEYSTORE'] = str(keystore)
    if not keystore.exists():
        subprocess.run([str(keytool), '-genkeypair', '-keystore', str(keystore), '-storetype', 'PKCS12',
                        '-storepass:env', 'GHOSTTRACK_STORE_PASSWORD', '-keypass:env', 'GHOSTTRACK_STORE_PASSWORD',
                        '-alias', 'ghosttrack', '-keyalg', 'RSA', '-keysize', '3072', '-validity', '10000',
                        '-dname', 'CN=GhostTrack, OU=Android, O=Serennity007'], env=env, check=True)
        if os.name != 'nt':
            keystore.chmod(0o600)
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-q'], cwd=root, check=True)
    subprocess.run([args.gradle, '-p', str(root / 'android'), '--no-daemon', '--max-workers=2',
                    ':app:assembleRelease', ':app:lintRelease'], cwd=root, env=env, check=True)
    apk = root / 'android/app/build/outputs/apk/release/app-release.apk'
    verifier = sdk / 'build-tools/36.0.0' / ('apksigner.bat' if os.name == 'nt' else 'apksigner')
    verification = subprocess.check_output([str(verifier), 'verify', '--verbose', '--print-certs', str(apk)],
                                            env=env, text=True, stderr=subprocess.STDOUT)
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)
    target = dist / f'GhostTrack-v{VERSION}-Android-universal.apk'
    shutil.copyfile(apk, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (dist / f'SHA256SUMS-Android-v{VERSION}.txt').write_text(f'{digest}  {target.name}\n', encoding='utf-8')
    (dist / f'Android-signature-v{VERSION}.txt').write_text(verification, encoding='utf-8')
    print(f'Built and verified: {target.name} ({target.stat().st_size:,} bytes)')
    print(f'Signing backup directory: {signing_dir}')


if __name__ == '__main__':
    main()
