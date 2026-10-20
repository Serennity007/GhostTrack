"""Query services used by the desktop application."""
import ipaddress
from urllib.parse import quote
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from platforms import lookup_profile


def query(kind, value, region='CN', language='zh', platform='Bilibili', cancel=None):
    value = value.strip()
    if kind == '国内平台':
        return lookup_profile(platform, value, cancel)
    if kind == '号码归属地':
        number = phonenumbers.parse(value, region)
        return {'国际格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                '归属地': geocoder.description_for_number(number, language),
                '运营商': carrier.name_for_number(number, language),
                '地区代码': phonenumbers.region_code_for_number(number),
                '时区': ', '.join(timezone.time_zones_for_number(number)),
                '有效号码': phonenumbers.is_valid_number(number),
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
    if not address.is_global:
        raise ValueError('请输入公网 IPv4 或 IPv6 地址，内网地址没有公网归属地')
    response = requests.get(f'https://ipwho.is/{address}', timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data.get('success'):
        raise ValueError(data.get('message', '服务未返回有效结果'))
    return {'IP': str(address), '国家': data.get('country'), '地区': data.get('region'),
            '城市': data.get('city'), '纬度': data.get('latitude'), '经度': data.get('longitude'),
            '网络服务商': data.get('connection', {}).get('isp'),
            '说明': 'IP 数据库估算位置，不代表设备实时位置'}

