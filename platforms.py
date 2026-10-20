"""Public profile normalization and bounded metadata fetches."""
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit

import requests


@dataclass(frozen=True)
class Platform:
    host: str
    prefix: str
    pattern: str
    aliases: tuple = ()
    short_hosts: tuple = ()


PLATFORMS = {
    'Douyin': Platform('www.douyin.com', 'user/', r'[A-Za-z0-9_-]{6,200}', ('douyin.com',), ('v.douyin.com',)),
    'Xiaohongshu': Platform('www.xiaohongshu.com', 'user/profile/', r'[0-9a-fA-F]{24}', ('xiaohongshu.com',), ('xhslink.com',)),
    'Kuaishou': Platform('www.kuaishou.com', 'profile/', r'[A-Za-z0-9_-]{1,100}', ('kuaishou.com',)),
    'Bilibili': Platform('space.bilibili.com', '', r'[0-9]{1,20}'),
    'Weibo': Platform('weibo.com', 'u/', r'[0-9]{1,20}', ('www.weibo.com',)),
    'Zhihu': Platform('www.zhihu.com', 'people/', r'[A-Za-z0-9_-]{1,100}', ('zhihu.com',)),
    'Douban': Platform('www.douban.com', 'people/', r'[A-Za-z0-9_-]{1,100}', ('douban.com',)),
}


class ProfileInputError(ValueError):
    def __init__(self, code='profile_input'):
        self.code = code
        super().__init__(code)


class QueryCancelled(Exception):
    pass


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise QueryCancelled()


def extract_input(value):
    value = value.strip()
    if not value or len(value) > 5000:
        raise ProfileInputError()
    matches = re.findall(r'https?://[^\s<>"\u3000]+', value)
    if len(matches) > 1:
        raise ProfileInputError('one_link')
    return matches[0].rstrip("。，,；;！!）)]}】'。") if matches else value


def detect_platform(value):
    value = extract_input(value)
    if '://' not in value:
        return None
    parsed = urlsplit(value)
    if parsed.username or parsed.password or parsed.port or parsed.fragment:
        raise ProfileInputError()
    host = parsed.netloc.lower()
    for name, spec in PLATFORMS.items():
        if host in (spec.host, *spec.aliases, *spec.short_hosts):
            if parsed.scheme != 'https' and not (parsed.scheme == 'http' and host in spec.short_hosts):
                raise ProfileInputError()
            return name
    raise ProfileInputError('unsupported_platform')


def profile_url(platform, value):
    if platform not in PLATFORMS:
        raise ProfileInputError('choose_platform')
    spec = PLATFORMS[platform]
    identifier = extract_input(value)
    query = ''
    if '://' in identifier:
        detected = detect_platform(identifier)
        parsed = urlsplit(identifier)
        if detected != platform or parsed.netloc.lower() in spec.short_hosts:
            raise ProfileInputError('profile_only')
        path = parsed.path.strip('/')
        if not path.startswith(spec.prefix):
            raise ProfileInputError('profile_only')
        identifier = path[len(spec.prefix):]
        # Keep only public sharing tokens needed by Xiaohongshu profile URLs.
        if platform == 'Xiaohongshu':
            pairs = [(k, v) for k, v in parse_qsl(parsed.query) if k in ('xsec_token', 'xsec_source') and len(v) <= 1024]
            query = ('?' + urlencode(pairs)) if pairs else ''
    if not re.fullmatch(spec.pattern, identifier):
        raise ProfileInputError('profile_input')
    suffix = '/' if spec.prefix == 'people/' else ''
    return f'https://{spec.host}/{spec.prefix}{identifier}{suffix}{query}'


def resolve_profile(platform, value, cancel=None):
    value = extract_input(value)
    detected = detect_platform(value)
    if detected:
        platform = detected
    if platform not in PLATFORMS:
        raise ProfileInputError('choose_platform')
    spec = PLATFORMS[platform]
    if '://' not in value or urlsplit(value).netloc.lower() not in spec.short_hosts:
        return platform, profile_url(platform, value)
    # Only the platform's own short-link and profile hosts may be requested.
    current = 'https://' + value.split('://', 1)[1]
    deadline = time.monotonic() + 25
    for _ in range(4):
        check_cancel(cancel)
        if time.monotonic() > deadline:
            raise requests.Timeout('Share-link resolution timed out')
        with requests.get(current, timeout=(5, 8), allow_redirects=False, stream=True,
                          headers={'User-Agent': 'GhostTrack-Desktop/1.3'}) as response:
            if response.status_code not in (301, 302, 303, 307, 308):
                raise ProfileInputError('short_link_failed')
            location = response.headers.get('Location', '')
            if not location:
                raise ProfileInputError('short_link_failed')
            target = urljoin(current, location)
            parsed_target = urlsplit(target)
            if parsed_target.scheme == 'http' and parsed_target.netloc.lower() in (spec.host, *spec.aliases, *spec.short_hosts):
                target = 'https://' + target.split('://', 1)[1]
            # Never request an arbitrary redirect target or a login/video page.
            try:
                detected = detect_platform(target)
            except (ValueError, TypeError):
                raise ProfileInputError('unsafe_redirect') from None
            if detected != platform:
                raise ProfileInputError('unsafe_redirect')
            if any(part in urlsplit(target).path for part in ('/login', '/passport', '/verify', '/captcha')):
                raise ProfileInputError('short_link_failed')
            if urlsplit(target).netloc.lower() not in spec.short_hosts:
                return platform, profile_url(platform, target)
            current = target
    raise ProfileInputError('short_link_failed')


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title = ''
        self.og_title = ''
        self.description = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            name = (attrs.get('property') or attrs.get('name') or '').lower()
            if name == 'og:title':
                self.og_title = (attrs.get('content') or '')[:300]
            if name in ('description', 'og:description'):
                self.description = (attrs.get('content') or '')[:500]

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = (self.title + data)[:300]


def lookup_profile(platform, value, cancel=None):
    original = extract_input(value)
    detected = detect_platform(original)
    if detected:
        platform = detected
    if platform not in PLATFORMS:
        raise ProfileInputError('choose_platform')
    result = {'平台': platform, '查询时间 UTC': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              '说明': '仅查询公开页面；未核实账号存在或身份归属'}
    try:
        platform, url = resolve_profile(platform, original, cancel)
    except ProfileInputError as error:
        if error.code != 'short_link_failed':
            raise
        result['主页链接'] = original
        result['页面状态'] = '访问受限或发生跳转；账号状态未知'
        return result
    except requests.RequestException:
        result['主页链接'] = original
        result['页面状态'] = '网络异常；请在浏览器中打开主页链接'
        return result
    result['主页链接'] = url
    try:
        check_cancel(cancel)
        started = time.monotonic()
        with requests.get(url, timeout=(5, 10), allow_redirects=False, stream=True,
                          headers={'User-Agent': 'GhostTrack-Desktop/1.3 (public-page-metadata)'}) as response:
            result['HTTP 状态'] = response.status_code
            if response.status_code == 404:
                result['页面状态'] = '页面未找到；无法确认账号是否存在'
                return result
            if response.status_code != 200:
                result['页面状态'] = '访问受限或发生跳转；账号状态未知'
                return result
            content_type = response.headers.get('Content-Type', '').lower()
            if 'html' not in content_type:
                result['页面状态'] = '未返回可解析的公开 HTML；账号状态未知'
                return result
            content = bytearray()
            for chunk in response.iter_content(8192):
                check_cancel(cancel)
                if time.monotonic() - started > 20:
                    raise requests.Timeout()
                remaining = 512 * 1024 - len(content)
                content.extend(chunk[:remaining])
                if len(content) >= 512 * 1024:
                    break
            encoding = response.encoding
            if not encoding or encoding.lower() == 'iso-8859-1':
                encoding = 'utf-8'
            parser = MetadataParser()
            parser.feed(content.decode(encoding, errors='replace'))
            title = ' '.join((parser.og_title or parser.title).split())
            description = ' '.join(parser.description.split())
            gate = (title + ' ' + description).lower()
            if any(marker in gate for marker in (
                    '登录', '安全验证', '验证码', '访问异常', '访问受限', 'please wait',
                    'passport', 'sign in', 'log in', 'captcha', 'security verification', 'sina visitor system')):
                result['页面状态'] = '需要登录或验证；账号状态未知'
            elif title.replace(' ', '').lower() in (
                    '抖音', '抖音-记录美好生活', '小红书-你的生活兴趣社区', '快手',
                    'bilibili', '微博', '知乎-有问题，就会有答案'):
                result['页面状态'] = '返回平台通用页面，未取得用户资料'
            elif title or description:
                result['页面标题'] = title or '—'
                result['公开简介'] = description or '—'
                result['页面状态'] = '已读取页面元信息；账号存在与身份仍未核实'
            else:
                result['页面状态'] = '页面需脚本加载或未提供元信息；账号状态未知'
    except (requests.RequestException, LookupError):
        result['页面状态'] = '网络异常；请在浏览器中打开主页链接'
    check_cancel(cancel)
    return result
