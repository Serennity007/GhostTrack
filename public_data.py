"""Public Internet resource lookups. No account correlation or contact harvesting."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import http.client
import ipaddress
import json
import re
import socket
import ssl
import time
from urllib.parse import quote, urlencode, urljoin, urlsplit

import requests

from platforms import MetadataParser, check_cancel


class PublicQueryError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def is_public_address(value):
    address = ipaddress.ip_address(value)
    return (address.is_global and not address.is_multicast and not address.is_reserved
            and not address.is_unspecified and not address.is_loopback and not address.is_link_local)


def domain_name(value):
    value = value.strip()
    if '://' in value:
        parts = urlsplit(value)
        if parts.scheme not in ('https', 'http') or parts.username or parts.password:
            raise PublicQueryError('invalid_domain')
        value = parts.hostname or ''
    try:
        value = value.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        raise PublicQueryError('invalid_domain') from None
    labels = value.split('.')
    if (len(value) > 253 or len(labels) < 2 or labels[-1].isdigit()
            or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in labels)
            or labels[-1] in ('local', 'localhost', 'internal', 'lan', 'home', 'test', 'invalid')):
        raise PublicQueryError('invalid_domain')
    return value


def api_json(url, cancel=None):
    check_cancel(cancel)
    with requests.get(url, headers={'User-Agent': 'GhostTrack-Desktop/1.4',
                                   'Accept': 'application/json'}, timeout=(5, 10), stream=True) as response:
        if response.status_code == 404:
            raise PublicQueryError('public_not_found')
        if response.status_code in (403, 429):
            raise PublicQueryError('public_rate_limit')
        response.raise_for_status()
        content = bytearray()
        started = time.monotonic()
        for chunk in response.iter_content(16384):
            check_cancel(cancel)
            content.extend(chunk)
            if len(content) > 1_048_576 or time.monotonic() - started > 20:
                raise PublicQueryError('source_unavailable')
        return json.loads(content), response.url


def registration(value, is_ip=False, cancel=None):
    resource = 'ip' if is_ip else 'domain'
    is_asn = is_ip and value.strip().upper().startswith('AS')
    if is_asn:
        match = re.fullmatch(r'AS([0-9]{1,10})', value.strip().upper())
        if not match or not 0 < int(match[1]) < 4294967296:
            raise PublicQueryError('invalid_asn')
        value = str(int(match[1]))
        resource = 'autnum'
    elif is_ip:
        address = ipaddress.ip_address(value.strip())
        if not is_public_address(address):
            raise PublicQueryError('public_address_only')
        value = str(address)
    else:
        value = domain_name(value)
    endpoint = f'https://rdap.org/{resource}/{quote(value, safe="")}'
    data, source = api_json(endpoint, cancel)
    result = {'来源链接': source, '注册状态': ', '.join(data.get('status', [])) or '—'}
    if is_asn:
        result.update({'ASN': 'AS' + value, '网络名称': data.get('name'), '网络标识': data.get('handle'),
                       '注册国家代码': data.get('country'), 'ASN 起始': data.get('startAutnum'),
                       'ASN 结束': data.get('endAutnum')})
    elif is_ip:
        result.update({'IP': value, '网络名称': data.get('name'), '网络标识': data.get('handle'),
                       '起始地址': data.get('startAddress'), '结束地址': data.get('endAddress'),
                       '注册国家代码': data.get('country'), '地址版本': data.get('ipVersion')})
        if data.get('startAddress') and data.get('endAddress'):
            result['CIDR'] = '\n'.join(str(network) for network in ipaddress.summarize_address_range(
                ipaddress.ip_address(data['startAddress']), ipaddress.ip_address(data['endAddress'])))
    else:
        result['域名'] = data.get('ldhName', value)
        result['名称服务器'] = '\n'.join(item.get('ldhName', '') for item in data.get('nameservers', [])[:20]) or '—'
        result['DNSSEC 已签名'] = data.get('secureDNS', {}).get('delegationSigned')
        for entity in data.get('entities', []):
            if 'registrar' in entity.get('roles', []):
                card = entity.get('vcardArray', [None, []])
                if len(card) == 2 and isinstance(card[1], list):
                    for field in card[1]:
                        if len(field) >= 4 and field[0] == 'fn' and isinstance(field[3], str):
                            result['注册商'] = field[3]
    for event in data.get('events', []):
        key = {'registration': '注册时间', 'expiration': '到期时间', 'last changed': '更新时间'}.get(event.get('eventAction'))
        if key:
            result[key] = event.get('eventDate')
    return result


def dns_records(value, cancel=None):
    name = domain_name(value)
    kinds = ('A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'CAA')
    result = {'域名': name, '来源链接': 'https://dns.google/query?' + urlencode({'name': name})}
    failures = []
    truncated_types = []
    def fetch(kind):
        check_cancel(cancel)
        try:
            data, _ = api_json('https://dns.google/resolve?' + urlencode({'name': name, 'type': kind}), cancel)
            rcode = data.get('Status', -1)
            all_records = data.get('Answer', [])
            records = all_records[:20]
            text = '\n'.join(f"{r.get('name', '')}  TTL={r.get('TTL', '')}  {r.get('data', '')}" for r in records)
            truncated = len(all_records) > 20 or len(text) > 6000
            text = text[:6000] + ('\n… [TRUNCATED]' if truncated else '')
            return kind, text or ('NXDOMAIN' if rcode == 3 else '—'), rcode not in (0, 3), truncated
        except (requests.RequestException, ValueError):
            return kind, 'ERROR', True, False
    with ThreadPoolExecutor(max_workers=4) as pool:
        for kind, text, failed, truncated in pool.map(fetch, kinds):
            check_cancel(cancel)
            result['DNS ' + kind] = text
            if failed:
                failures.append(kind)
            if truncated:
                truncated_types.append(kind)
    result['查询状态'] = '部分来源不可用' if failures else '已完成'
    if failures:
        result['失败记录类型'] = ', '.join(failures)
    if truncated_types:
        result['截断记录类型'] = ', '.join(truncated_types)
    return result


def github_profile(value, cancel=None):
    name = value.strip()
    if name.startswith('https://github.com/'):
        parsed = urlsplit(name)
        if parsed.query or parsed.fragment:
            raise PublicQueryError('invalid_github')
        name = parsed.path.strip('/')
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', name):
        raise PublicQueryError('invalid_github')
    data, source = api_json(f'https://api.github.com/users/{name}', cancel)
    result = {'主页链接': f'https://github.com/{name}', '来源链接': source,
              '用户名': data.get('login'), '显示名称': data.get('name'), '公开简介': data.get('bio'),
              '账号类型': data.get('type'), '公开仓库数': data.get('public_repos'),
              '粉丝数': data.get('followers'), '关注数': data.get('following'),
              '注册时间': data.get('created_at'), '更新时间': data.get('updated_at')}
    try:
        repos, _ = api_json(f'https://api.github.com/users/{name}/repos?sort=updated&per_page=5', cancel)
        result['最近公开仓库'] = '\n'.join(f"{r.get('full_name', '')} | {r.get('language') or '—'} | stars={r.get('stargazers_count', 0)}\n{r.get('html_url', '')}" for r in repos[:5]) or '—'
        result['查询状态'] = '已完成'
    except (requests.RequestException, ValueError):
        result['查询状态'] = '部分来源不可用'
    return result


def public_target(value):
    value = value.strip()
    if '://' not in value:
        value = 'https://' + value
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or parsed.username or parsed.password or parsed.fragment
            or parsed.port not in (None, 443) or len(value) > 4096):
        raise PublicQueryError('https_public_only')
    try:
        address = ipaddress.ip_address(parsed.hostname or '')
    except ValueError:
        host = domain_name(parsed.hostname or '')
    else:
        if not is_public_address(address):
            raise PublicQueryError('public_address_only')
        host = str(address)
    return value, host, (parsed.path or '/') + (('?' + parsed.query) if parsed.query else '')


def public_addresses(host, cancel=None):
    check_cancel(cancel)
    entries = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    check_cancel(cancel)
    addresses = list(dict.fromkeys(item[4][0] for item in entries))
    # Some local DNS/proxy clients map all public names into the benchmarking
    # pool. Resolve the public name via DoH instead; never connect to that pool.
    fake_pool = ipaddress.ip_network('198.18.0.0/15')
    if addresses and all(ipaddress.ip_address(address).version == 4 and ipaddress.ip_address(address) in fake_pool
                         for address in addresses):
        data, _ = api_json('https://dns.google/resolve?' + urlencode({'name': host, 'type': 'A'}), cancel)
        addresses = [r['data'] for r in data.get('Answer', []) if r.get('type') == 1]
    if not addresses or any(not is_public_address(address) for address in addresses):
        raise PublicQueryError('public_address_only')
    return addresses


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, address):
        super().__init__(host, port=443, timeout=8, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def website_info(value, cancel=None):
    current, _, _ = public_target(value)
    chain = []
    started = time.monotonic()
    for _ in range(4):
        check_cancel(cancel)
        current, host, path = public_target(current)
        address = public_addresses(host, cancel)[0]
        check_cancel(cancel)
        connection = PinnedHTTPS(host, address)
        try:
            connection.connect()
            certificate = connection.sock.getpeercert()
            connection.request('GET', path, headers={'User-Agent': 'GhostTrack-Desktop/1.4', 'Accept': 'text/html'})
            response = connection.getresponse()
            chain.append(f'{response.status} {current}')
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader('Location')
                if not location:
                    raise PublicQueryError('source_unavailable')
                current = urljoin(current, location)
                continue
            body = bytearray()
            while len(body) < 131072:
                check_cancel(cancel)
                if time.monotonic() - started > 25:
                    raise PublicQueryError('source_unavailable')
                chunk = response.read(min(16384, 131072 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
            metadata = MetadataParser()
            content_type = response.getheader('Content-Type', '')
            encoding_hint = re.search(r'charset\s*=\s*["\x27]?([A-Za-z0-9._-]+)',
                                      content_type + ' ' + body[:4096].decode('ascii', errors='ignore'), re.I)
            encoding = encoding_hint[1] if encoding_hint else 'utf-8'
            try:
                decoded = body.decode(encoding, errors='replace')
            except LookupError:
                decoded = body.decode('utf-8', errors='replace')
            metadata.feed(decoded)
            issuer = ', '.join(v for entry in certificate.get('issuer', ()) for k, v in entry if k in ('organizationName', 'commonName'))
            expires = certificate.get('notAfter', '')
            days = int((ssl.cert_time_to_seconds(expires) - time.time()) / 86400) if expires else None
            result = {'来源链接': current, 'HTTP 状态': response.status, '连接地址': address,
                      '页面标题': ' '.join(metadata.title.split()) or '—',
                      '响应类型': response.getheader('Content-Type', '—'),
                      '服务器标识': response.getheader('Server', '—'),
                      '跳转链': '\n'.join(chain), '响应耗时 ms': round((time.monotonic() - started) * 1000),
                      '证书颁发者': issuer or '—', '证书生效时间': certificate.get('notBefore'),
                      '证书到期时间': expires, '证书剩余天数': days,
                      '证书覆盖域名': ', '.join(v for k, v in certificate.get('subjectAltName', ()) if k == 'DNS')[:3000]}
            for header in ('Strict-Transport-Security', 'Content-Security-Policy', 'X-Content-Type-Options', 'Referrer-Policy'):
                result[header] = response.getheader(header, '—')[:3000]
            result['查询状态'] = '已完成' if response.status < 400 else '部分来源不可用'
            return result
        except ssl.SSLError:
            raise PublicQueryError('tls_failed') from None
        finally:
            connection.close()
    raise PublicQueryError('redirect_limit')
