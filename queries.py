"""Query services used by the desktop application."""
import ipaddress
from urllib.parse import quote
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from archive import flatten
from platforms import lookup_profile
from public_data import registration, dns_records, github_profile, website_info, is_public_address, domain_overview

ARCHIVE_DISPLAY_LIMIT = 12


def query(kind, value, region='CN', language='zh', platform='Bilibili', cancel=None, progress=None, archive=None):
    value = value.strip()
    if kind == '授权账号档案':
        if archive is None:
            raise ValueError('archive unavailable')
        matches = archive.search(value)
        result = {'匹配记录数': len(matches),
                  '说明': '仅含本人授权或公开主页保存的关联，不代表实时验证结果'}
        if not matches:
            result['提示'] = '没有匹配记录；在平台查询结果中可保存授权关联'
            return result
        result['显示记录数'] = min(len(matches), ARCHIVE_DISPLAY_LIMIT)
        result.update(flatten(matches[:ARCHIVE_DISPLAY_LIMIT]))
        if len(matches) > ARCHIVE_DISPLAY_LIMIT:
            result['提示'] = '仅显示前 12 条；打开档案管理可查看或导出全部'
        return result
    if kind == '域名综合报告':
        return domain_overview(value, cancel, progress)
    if kind == '域名档案':
        return registration(value, cancel=cancel)
    if kind == 'DNS 记录':
        return dns_records(value, cancel)
    if kind == '网站与证书':
        return website_info(value, cancel)
    if kind == 'IP 注册网络':
        return registration(value, is_ip=True, cancel=cancel)
    if kind == 'GitHub 公开资料':
        return github_profile(value, cancel)
    if kind == '国内平台':
        return lookup_profile(platform, value, cancel)
    if kind == '号码归属地':
        number = phonenumbers.parse(value, region)
        return {'国际格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'E.164 格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
                '国内格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL),
                '国家呼叫码': number.country_code,
                '归属地': geocoder.description_for_number(number, language),
                '运营商': carrier.name_for_number(number, language),
                '地区代码': phonenumbers.region_code_for_number(number),
                '时区': ', '.join(timezone.time_zones_for_number(number)),
                '有效号码': phonenumbers.is_valid_number(number),
                '可能有效': phonenumbers.is_possible_number(number),
                '说明': '号码段元数据，不代表持有人身份或实时位置'}
    if kind == '用户名链接':
        if not value or len(value) > 100 or any(c.isspace() for c in value):
            raise ValueError('请输入不含空白的用户名（1–100 字符）')
        name = quote(value, safe='')
        return {'GitHub': f'https://github.com/{name}',
                'Instagram': f'https://www.instagram.com/{name}/',
                'X': f'https://x.com/{name}',
                '说明': '仅生成公开主页链接；未核实账号存在或身份归属'}
    if kind == '本机公网 IP':
        response = requests.get('https://api.ipify.org', timeout=15)
        response.raise_for_status()
        return {'公网 IP': str(ipaddress.ip_address(response.text.strip()))}
    address = ipaddress.ip_address(value)
    if not is_public_address(address):
        raise ValueError('请输入公网 IPv4 或 IPv6 地址，内网地址没有公网归属地')
    response = requests.get(f'https://ipwho.is/{address}', timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data.get('success'):
        raise ValueError(data.get('message', '服务未返回有效结果'))
    return {'IP': str(address), '国家': data.get('country'), '地区': data.get('region'),
            '城市': data.get('city'), '纬度': data.get('latitude'), '经度': data.get('longitude'),
            '网络服务商': data.get('connection', {}).get('isp'),
            '网络组织': data.get('connection', {}).get('org'),
            'ASN': data.get('connection', {}).get('asn'),
            '网络域名': data.get('connection', {}).get('domain'),
            '洲': data.get('continent'), '邮政编码': data.get('postal'),
            '时区': data.get('timezone', {}).get('id'),
            '说明': 'IP 数据库估算位置，不代表设备实时位置'}

