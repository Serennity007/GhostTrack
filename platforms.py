"""Fetch public profile page metadata without login or access-control bypass."""
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit

import requests

PLATFORMS = {
    'Bilibili': ('space.bilibili.com', '', True),
    'Weibo': ('weibo.com', 'u/', True),
    'Zhihu': ('www.zhihu.com', 'people/', False),
    'Douban': ('www.douban.com', 'people/', False),
}


def profile_url(platform, value):
    if platform not in PLATFORMS:
        raise ValueError('Unknown platform')
    host, prefix, numeric = PLATFORMS[platform]
    identifier = value.strip()
    if '://' in identifier:
        parsed = urlsplit(identifier)
        if (parsed.scheme != 'https' or parsed.netloc.lower() != host
                or parsed.query or parsed.fragment):
            raise ValueError('Use a canonical HTTPS profile URL')
        path = parsed.path.strip('/')
        if not path.startswith(prefix):
            raise ValueError('Invalid profile URL path')
        identifier = path[len(prefix):]
    pattern = r'[0-9]{1,20}' if numeric else r'[A-Za-z0-9_-]{1,100}'
    if not re.fullmatch(pattern, identifier):
        raise ValueError('Enter the UID or profile identifier, not the display name')
    return f'https://{host}/{prefix}{identifier}' + ('/' if prefix == 'people/' else '')


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
                self.og_title = attrs.get('content', '')[:300]
            if name in ('description', 'og:description'):
                self.description = attrs.get('content', '')[:500]

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = (self.title + data)[:300]


def lookup_profile(platform, value):
    url = profile_url(platform, value)
    result = {'平台': platform, '主页链接': url,
              '查询时间 UTC': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              '说明': '仅查询公开页面；未核实账号存在或身份归属'}
    try:
        started = time.monotonic()
        with requests.get(url, timeout=(8, 12), allow_redirects=False, stream=True,
                          headers={'User-Agent': 'GhostTrack-Desktop/1.2 (public-page-metadata)'}) as response:
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
                if time.monotonic() - started > 20:
                    result['页面状态'] = '网络异常；请在浏览器中打开主页链接'
                    return result
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
            gate_text = (title + ' ' + description).lower()
            if any(marker in gate_text for marker in (
                    '登录', '安全验证', '验证码', '访问异常', '访问受限',
                    'passport', 'sign in', 'log in', 'captcha', 'security verification')):
                result['页面状态'] = '需要登录或验证；账号状态未知'
            elif title or description:
                result['页面标题'] = title or '—'
                result['公开简介'] = description or '—'
                result['页面状态'] = '已读取页面元信息；账号存在与身份仍未核实'
            else:
                result['页面状态'] = '页面需脚本加载或未提供元信息；账号状态未知'
    except (requests.RequestException, LookupError):
        result['页面状态'] = '网络异常；请在浏览器中打开主页链接'
    return result
