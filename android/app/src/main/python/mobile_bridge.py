"""JSON boundary for Android; public query services stay shared with desktop."""
import csv
from datetime import datetime, timezone
import html
import io
import json
import os

import certifi
import phonenumbers

from i18n import LANGUAGES, UI, localize, platform_name
from platforms import PLATFORMS, ProfileInputError, QueryCancelled, check_cancel
from public_data import PublicQueryError
from queries import query
from reports import spreadsheet_cell
from version import VERSION


# requests already uses certifi. The shared pinned HTTPS client uses stdlib SSL,
# whose Android build must see the same packaged CA bundle for verified TLS.
os.environ.setdefault('SSL_CERT_FILE', certifi.where())


# Stable IDs are the same canonical tool names used by the desktop and reports.
TOOLS = (
    ('IP 归属地', 'ip', 'hint_ip', '8.8.8.8', 'ipwho.is'),
    ('本机公网 IP', 'self', 'hint_self', '', 'api.ipify.org'),
    ('号码归属地', 'phone', 'hint_phone', '+12025550123', 'libphonenumber'),
    ('用户名链接', 'username', 'hint_username', 'octocat', 'GitHub / Instagram / X'),
    ('国内平台', 'domestic', 'hint_share', 'https://space.bilibili.com/2', 'Public profile HTML'),
    ('域名档案', 'domain', 'hint_domain', 'python.org', 'RDAP'),
    ('DNS 记录', 'dns', 'hint_dns', 'python.org', 'DNS over HTTPS'),
    ('网站与证书', 'website', 'hint_website', 'https://www.python.org/', 'HTTPS / TLS'),
    ('IP 注册网络', 'network', 'hint_network', 'AS15169', 'RDAP / IANA'),
    ('GitHub 公开资料', 'github', 'hint_github', 'octocat', 'GitHub REST API'),
    ('域名综合报告', 'overview', 'hint_overview', 'python.org', 'RDAP + DNS + HTTPS'),
)

MOBILE_UI = {
    'language': ('界面语言', 'Language', '表示言語', 'Idioma'),
    'title': ('公开信息控制台', 'PUBLIC DATA CONSOLE', '公開情報コンソール', 'CONSOLA DE DATOS PÚBLICOS'),
    'export_type': ('选择报告格式', 'Report format', 'レポート形式', 'Formato del informe'),
    'share': ('分享报告', 'Share report', 'レポートを共有', 'Compartir informe'),
    'source': ('公开来源', 'Public source', '公開情報源', 'Fuente pública'),
    'public_profile_source': ('公开主页 HTML', 'Public profile HTML', '公開プロフィール HTML', 'HTML de perfil público'),
    'region_label': ('号码地区代码（如 CN、US、JP）', 'Phone region code (CN, US, JP)', '電話番号の地域コード（CN・US・JP）', 'Código de región (CN, US, JP)'),
    'empty_input': ('请输入查询目标', 'Enter a query target', '検索対象を入力してください', 'Introduce un destino de consulta'),
    'query_details': ('查询详情', 'Query details', '検索の詳細', 'Detalles de la consulta'),
    'export_json': ('JSON 数据', 'JSON data', 'JSON データ', 'Datos JSON'),
    'export_csv': ('CSV 表格', 'CSV spreadsheet', 'CSV 表', 'Hoja CSV'),
    'export_html': ('HTML 报告', 'HTML report', 'HTML レポート', 'Informe HTML'),
    'help_body': (
        '选择工具，输入目标或填入示例后开始查询。国内平台支持抖音、小红书、快手、B站、微博、知乎、豆瓣的公开主页链接；视频和笔记链接不是个人主页。\n\n点击结果旁的复制按钮可复制单项，也可复制全部、筛选字段，或保存 JSON / CSV / HTML 报告。取消后迟到的请求不会覆盖新结果。\n\n仅使用公开数据。平台要求登录、验证或脚本时，仅保留可读取的信息和访问状态。号码/IP 归属地不是实时位置；不提供由手机号查找个人账号。',
        'Choose a tool and enter a target or use Example. Chinese platforms support public profile URLs from Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu and Douban; video and post links are not profiles.\n\nUse the Copy button beside a result to copy its value, copy all, filter fields, or save JSON / CSV / HTML reports. Late cancelled requests cannot replace newer results.\n\nPublic data only. Login, verification and scripted pages may provide limited information. Phone/IP regions are not live locations; phone-to-account identification is not provided.',
        'ツールを選び、対象を入力するか入力例を使用してください。抖音、小紅書、快手、Bilibili、Weibo、知乎、豆瓣の公開プロフィール URL に対応します。動画・投稿リンクはプロフィールではありません。\n\n各結果のコピーボタンで値をコピーできます。全件コピー、絞り込み、JSON / CSV / HTML の保存にも対応します。中止した応答は新しい結果を上書きしません。\n\n公開情報のみ使用します。ログイン・認証・スクリプトが必要なページは情報が制限されます。電話番号・IP の地域は現在地ではありません。電話番号から個人アカウントを特定する機能はありません。',
        'Elige una herramienta e introduce un destino o usa Ejemplo. Admite perfiles públicos de Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu y Douban; los enlaces de vídeos y publicaciones no son perfiles.\n\nUsa el botón Copiar junto al resultado para copiar su valor, copia todo, filtra campos o guarda informes JSON / CSV / HTML. Las respuestas canceladas no sustituyen resultados nuevos.\n\nSolo datos públicos. Las páginas con acceso, verificación o scripts pueden ofrecer datos limitados. Las regiones de teléfono/IP no son ubicaciones en vivo; no se identifican cuentas personales a partir de un teléfono.',
    ),
}


def _language(language):
    return language if language in UI else 'zh'


def _dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def bootstrap(lang='zh'):
    """Return all content needed to build the native, four-language interface."""
    lang = _language(lang)
    strings = dict(UI[lang])
    index = ('zh', 'en', 'ja', 'es').index(lang)
    strings.update({key: values[index] for key, values in MOBILE_UI.items()})
    return _dumps({
        'version': VERSION,
        'languages': [{'code': code, 'label': label} for label, code in LANGUAGES.items()],
        'tools': [{'id': tool, 'title': UI[lang][key], 'hint': UI[lang][hint],
                   'example': example,
                   'source': strings['public_profile_source'] if key == 'domestic' else source}
                  for tool, key, hint, example, source in TOOLS],
        'platforms': [{'id': name, 'label': platform_name(name, lang)}
                      for name in ('Auto', *PLATFORMS)],
        'ui': strings,
    })


class _Cancellation:
    """Adapt Java AtomicBoolean without importing Java in Python unit tests."""
    def __init__(self, flag):
        self.flag = flag

    def is_set(self):
        if self.flag is None:
            return False
        if hasattr(self.flag, 'get'):
            return bool(self.flag.get())
        return bool(self.flag.is_set())


def _key(key, language):
    if ' / ' in key:
        prefix, suffix = key.split(' / ', 1)
        return prefix + ' / ' + _key(suffix, language)
    return str(localize(key, language))


def _value(key, value, language):
    if key == '平台' and value in PLATFORMS:
        return platform_name(value, language)
    if key.endswith('失败原因') and isinstance(value, str) and value in UI[language]:
        return UI[language][value]
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(localize(value, language))


def _error(code, language, cancelled=False):
    if code not in UI[language]:
        code = 'network_error'
    return _dumps({'ok': False, 'result': {}, 'raw': {},
                   'error': {'code': code, 'message': UI[language][code]},
                   'cancelled': cancelled})


def run_query(kind, value, region='CN', language='zh', platform='Auto', cancel=None):
    """Run a shared query and return localized results, never Python exceptions."""
    language = _language(language)
    token = _Cancellation(cancel)
    try:
        check_cancel(token)
        if kind not in {tool[0] for tool in TOOLS}:
            return _error('input_error', language)
        if not isinstance(value, str) or len(value) > 5000:
            return _error('input_error', language)
        if not value.strip() and kind != '本机公网 IP':
            return _error('input_error', language)
        if platform not in ('Auto', *PLATFORMS):
            return _error('unsupported_platform', language)
        data = query(kind, value, region=str(region).strip().upper(),
                     language=language, platform=platform, cancel=token)
        check_cancel(token)
        raw = dict(data)
        raw.update({'查询工具': kind, '查询输入': value.strip(),
                    '查询时间 UTC': datetime.now(timezone.utc).isoformat(timespec='seconds')})
        result = {_key(key, language): _value(key, value, language)
                  for key, value in raw.items()}
        return _dumps({'ok': True, 'result': result, 'raw': raw,
                       'error': None, 'cancelled': False})
    except QueryCancelled:
        return _error('cancelled', language, cancelled=True)
    except (ProfileInputError, PublicQueryError) as error:
        return _error(error.code, language)
    except (ValueError, phonenumbers.NumberParseException):
        return _error('input_error', language)
    except Exception:
        # Network/SSL/provider exceptions must not leak stack traces or private paths.
        return _error('network_error', language)


def render_report(result_json, format):
    """Produce shareable report text without Android storage paths or temp files."""
    data = json.loads(result_json)
    if isinstance(data, dict) and 'ok' in data and 'result' in data:
        if not data['ok']:
            raise ValueError('No successful result to export')
        data = data['result']
    if not isinstance(data, dict):
        raise ValueError('Report must contain result fields')
    format = str(format).lower().lstrip('.')
    if format == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    if format == 'csv':
        stream = io.StringIO(newline='')
        writer = csv.writer(stream)
        writer.writerow(('Field', 'Value'))
        writer.writerows((spreadsheet_cell(key), spreadsheet_cell(value))
                         for key, value in data.items())
        return '\ufeff' + stream.getvalue()
    if format == 'html':
        rows = ''.join('<tr><th>' + html.escape(str(key)) + '</th><td>'
                       + html.escape(str(value)) + '</td></tr>'
                       for key, value in data.items())
        return ('<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '<title>GhostTrack report</title><style>'
                'body{background:#070d0b;color:#e3f9ee;font:16px system-ui,sans-serif;'
                'margin:32px auto;padding:0 20px;max-width:1000px}'
                'h1{color:#a3ff6f;font-family:monospace}small{color:#91ac9d}'
                'table{border-collapse:collapse;width:100%;margin:28px 0}'
                'th,td{text-align:left;vertical-align:top;border-bottom:1px solid #284235;'
                'padding:14px;overflow-wrap:anywhere;white-space:pre-wrap}'
                'th{width:28%;color:#91ac9d}tr:nth-child(odd){background:#0d1915}'
                '@media print{body{background:white;color:black}h1,th{color:black}}'
                '</style></head><body><h1>GHOST//TRACK</h1><small>Android report · '
                + html.escape(VERSION) + '</small><table>' + rows + '</table></body></html>')
    raise ValueError('Unsupported report format')
