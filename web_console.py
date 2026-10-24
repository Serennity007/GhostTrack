"""Loopback-only Atlas service. Reuses the public-data engine; stores no reports."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import ipaddress
import json
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlsplit
import webbrowser

import requests
from i18n import localize
from platforms import QueryCancelled
from public_data import api_json, dns_records, domain_name, github_profile, registration, website_info
from queries import query
from version import VERSION

WEB_ROOT = Path(__file__).resolve().parent / 'web'
TOOLS = ('overview', 'dns', 'domain', 'website', 'network', 'github', 'phone', 'username', 'location', 'domestic')
KINDS = {'phone': '号码归属地', 'username': '用户名链接', 'location': 'IP 归属地', 'domestic': '国内平台'}
SAFE_ERROR = {'invalid_domain', 'invalid_asn', 'invalid_github', 'public_address_only', 'public_not_found',
              'public_rate_limit', 'source_unavailable', 'https_public_only', 'tls_failed', 'redirect_limit', 'invalid_input'}


def _fields(data):
    result = {}
    for key, value in data.items():
        label = localize(key, 'en')
        label = {'Expires at': 'Expires', 'Registered at': 'Registered', 'Updated at': 'Updated',
                 'Response time (ms)': 'Response time ms'}.get(label, label)
        result[label] = localize(value, 'en') if isinstance(value, str) else value
    return result


def _source(identity, operation, cancel):
    start = time.monotonic()
    try:
        if cancel.is_set():
            raise QueryCancelled()
        data = operation()
        if cancel.is_set():
            raise QueryCancelled()
        fields = _fields(data)
        partial = (data.get('查询状态') == '部分来源不可用' or
                   identity == 'PROFILE' and data.get('页面状态') != '已读取页面元信息；账号存在与身份仍未核实')
        return {'id': identity, 'status': 'partial' if partial else 'ok',
                'fields': fields, 'url': data.get('来源链接', data.get('主页链接', '')),
                'elapsedMs': round((time.monotonic() - start) * 1000)}
    except QueryCancelled:
        return {'id': identity, 'status': 'cancelled', 'fields': {}, 'error': 'cancelled'}
    except Exception as error:
        code = getattr(error, 'code', 'invalid_input' if identity in ('PHONE', 'USERNAME') else 'source_unavailable')
        if code not in SAFE_ERROR:
            code = 'source_unavailable'
        return {'id': identity, 'status': 'rate_limited' if code == 'public_rate_limit' else 'error',
                'fields': {}, 'error': code, 'elapsedMs': round((time.monotonic() - start) * 1000)}


def run_lookup(payload, cancel=None):
    tool, target = payload.get('tool'), payload.get('target')
    if tool not in TOOLS or not isinstance(target, str) or not target.strip() or len(target) > 4096:
        raise ValueError('invalid_input')
    target = target.strip()
    region, platform = payload.get('region', 'CN'), payload.get('platform', 'Auto')
    if not isinstance(region, str) or not re.fullmatch('[A-Z]{2}', region) or not isinstance(platform, str) or len(platform) > 40:
        raise ValueError('invalid_input')
    cancel = cancel or threading.Event()
    start = time.monotonic()
    if tool in ('overview', 'dns', 'domain'):
        target = domain_name(target)
    actions = {
        'RDAP': lambda: registration(target, cancel=cancel),
        'DNS': lambda: dns_records(target, cancel),
        'HTTPS': lambda: website_info('https://' + target + '/', cancel),
    }
    if tool == 'overview':
        with ThreadPoolExecutor(max_workers=3) as pool:
            jobs = [pool.submit(_source, key, action, cancel) for key, action in actions.items()]
            sources = [job.result() for job in jobs]
    else:
        identity, operation = {
            'domain': ('RDAP', actions['RDAP']), 'dns': ('DNS', actions['DNS']),
            'website': ('HTTPS', lambda: website_info(target, cancel)),
            'network': ('NETWORK', lambda: registration(target, is_ip=True, cancel=cancel)),
            'github': ('GITHUB', lambda: github_profile(target, cancel)),
            **{key: ({'phone': 'PHONE', 'username': 'USERNAME', 'location': 'LOCATION', 'domestic': 'PROFILE'}[key],
                     lambda k=key: query(KINDS[k], target, region=region, language='en', platform=platform, cancel=cancel))
               for key in KINDS},
        }[tool]
        sources = [_source(identity, operation, cancel)]
    return {'schema': 1, 'version': VERSION, 'id': payload.get('id') or secrets.token_hex(12), 'tool': tool,
            'target': target, 'region': region, 'platform': platform, 'at': datetime.now(timezone.utc).isoformat(),
            'elapsedMs': round((time.monotonic() - start) * 1000), 'sources': sources,
            'runtime': 'local', 'privacy': 'No server-side query history; explicit browser saves only.'}


def release_updates():
    data, _ = api_json('https://api.github.com/repos/Serennity007/GhostTrack/releases?per_page=30')
    releases = []
    for platform in ('windows', 'android'):
        candidates = []
        for release in data if isinstance(data, list) else []:
            match = re.fullmatch(platform + r'-v([0-9]+\.[0-9]+\.[0-9]+)', release.get('tag_name', ''))
            if match and not release.get('draft') and not release.get('prerelease'):
                candidates.append((tuple(map(int, match[1].split('.'))), match[1], release))
        if candidates:
            _, number, release = max(candidates, key=lambda item: item[0])
            url = release.get('html_url', '')
            if url.startswith('https://github.com/Serennity007/GhostTrack/releases/tag/'):
                releases.append({'platform': platform, 'version': number, 'url': url})
    return {'current': VERSION, 'releases': releases, 'checkedAt': datetime.now(timezone.utc).isoformat()}


class AtlasServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, port=0):
        self.token = secrets.token_urlsafe(32)
        self.slots = threading.BoundedSemaphore(2)
        self.lock = threading.Lock()
        self.active = {}
        self.calls = deque()
        super().__init__(('127.0.0.1', port), AtlasHandler)

    @property
    def origin(self):
        return f'http://127.0.0.1:{self.server_port}'


class AtlasHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *_):
        pass  # Never record paths, inputs, tokens or results.

    def send(self, status, content, content_type='application/json; charset=utf-8'):
        body = content if isinstance(content, bytes) else json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        for key, value in {'Content-Type': content_type, 'Content-Length': str(len(body)), 'Cache-Control': 'no-store',
                           'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
                           'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"}.items():
            self.send_header(key, value)
        if status == 429:
            self.send_header('Retry-After', '5')
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def do_GET(self):
        if not self.valid_host():
            return self.send(403, {'error': 'invalid_origin'})
        path = urlsplit(self.path).path
        if path == '/api/meta':
            return self.send(200, {'version': VERSION, 'runtime': 'local', 'tools': list(TOOLS), 'token': self.server.token,
                                   'limits': {'batch': 50, 'requestsPerMinute': 60}, 'website': True})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.mjs': ('app.mjs', 'text/javascript; charset=utf-8'),
                  '/core.mjs': ('core.mjs', 'text/javascript; charset=utf-8'), '/lang.mjs': ('lang.mjs', 'text/javascript; charset=utf-8'),
                  '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if path in assets:
            name, mime = assets[path]
            return self.send(200, (WEB_ROOT / name).read_bytes(), mime)
        return self.send(404, {'error': 'not_found'})

    def do_POST(self):
        if (not self.valid_host() or self.headers.get('Origin') != self.server.origin or
                not secrets.compare_digest(self.headers.get('X-GhostTrack-Token', ''), self.server.token)):
            self.close_connection = True
            return self.send(403, {'error': 'invalid_origin'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json' or self.headers.get('Transfer-Encoding'):
            self.close_connection = True
            return self.send(415, {'error': 'json_required'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                raise ValueError()
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError()
        except (ValueError, UnicodeError):
            self.close_connection = True
            return self.send(400, {'error': 'invalid_input'})
        path = urlsplit(self.path).path
        identifier = payload.get('id', '')
        if not isinstance(identifier, str) or not re.fullmatch('[A-Za-z0-9-]{1,80}', identifier):
            return self.send(400, {'error': 'invalid_input'})
        if path == '/api/cancel':
            with self.server.lock:
                event = self.server.active.get(identifier)
                if event:
                    event.set()
            return self.send(200, {'cancelled': bool(event)})
        if path not in ('/api/query', '/api/updates'):
            return self.send(404, {'error': 'not_found'})
        with self.server.lock:
            now = time.monotonic()
            while self.server.calls and now - self.server.calls[0] > 60:
                self.server.calls.popleft()
            if len(self.server.calls) >= 60 or identifier in self.server.active:
                return self.send(429, {'error': 'rate_limited'})
            self.server.calls.append(now)
            cancel = threading.Event()
            self.server.active[identifier] = cancel
        if not self.server.slots.acquire(blocking=False):
            with self.server.lock:
                self.server.active.pop(identifier, None)
            return self.send(429, {'error': 'busy'})
        try:
            self.connection.settimeout(90)
            result = release_updates() if path == '/api/updates' else run_lookup(payload, cancel)
            self.send(200, result)
        except (ValueError, requests.RequestException):
            self.send(400 if path == '/api/query' else 502, {'error': 'invalid_input' if path == '/api/query' else 'source_unavailable'})
        except Exception:
            self.send(502, {'error': 'source_unavailable'})
        finally:
            self.server.slots.release()
            with self.server.lock:
                self.server.active.pop(identifier, None)


def start_console(port=0, open_browser=True):
    server = AtlasServer(port)
    thread = threading.Thread(target=server.serve_forever, name='GhostTrack-Atlas', daemon=True)
    thread.start()
    if open_browser:
        webbrowser.open(server.origin)
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    server = start_console(args.port, not args.no_browser)
    print('GhostTrack Atlas: ' + server.origin, flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
