"""Android JSON boundary tests; no Android runtime or network required."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

from platforms import QueryCancelled
from public_data import PublicQueryError


BRIDGE_PATH = Path(__file__).parent / 'android/app/src/main/python/mobile_bridge.py'
SPEC = importlib.util.spec_from_file_location('mobile_bridge', BRIDGE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


class JavaBoolean:
    def __init__(self, value=False):
        self.value = value

    def get(self):
        return self.value


class MobileBridgeTests(unittest.TestCase):
    def test_bootstrap_has_stable_modules_and_four_language_ui(self):
        canonical = [tool[0] for tool in bridge.TOOLS]
        self.assertEqual(len(canonical), 11)
        titles = []
        for language in ('zh', 'en', 'ja', 'es'):
            data = json.loads(bridge.bootstrap(language))
            self.assertEqual([tool['id'] for tool in data['tools']], canonical)
            self.assertEqual({x['code'] for x in data['languages']}, {'zh', 'en', 'ja', 'es'})
            self.assertEqual(len(data['platforms']), 8)
            for tool in data['tools']:
                self.assertTrue(tool['title'] and tool['hint'] and tool['source'])
            for key in ('run', 'cancel', 'copy', 'copy_selected', 'export', 'paste',
                        'example', 'filter', 'language', 'share', 'help_body'):
                self.assertTrue(data['ui'][key])
            titles.append(data['tools'][-1]['title'])
        self.assertEqual(len(set(titles)), 4)
        self.assertEqual(json.loads(bridge.bootstrap('bad'))['ui']['run'], '开始查询')

    def test_query_localizes_namespaces_and_retains_canonical_metadata(self):
        raw = {'RDAP / 注册商': 'Example Ltd', 'DNS / DNSSEC 已签名': True,
               'HTTPS / 页面内容状态': 'content_parsed',
               'DNS / 失败原因': 'source_unavailable', '查询状态': '部分来源不可用'}
        with patch.object(bridge, 'query', return_value=raw) as query:
            result = json.loads(bridge.run_query('域名综合报告', ' python.org ', 'jp', 'en'))
        self.assertTrue(result['ok'])
        self.assertIsNone(result['error'])
        self.assertEqual(result['result']['RDAP / Registrar'], 'Example Ltd')
        self.assertEqual(result['result']['DNS / DNSSEC delegation signed'], 'Yes')
        self.assertEqual(result['result']['HTTPS / Page content status'], 'Content parsed')
        self.assertEqual(result['result']['DNS / Failure reason'], bridge.UI['en']['source_unavailable'])
        self.assertEqual(result['raw']['查询输入'], 'python.org')
        self.assertEqual(result['raw']['查询工具'], '域名综合报告')
        self.assertRegex(result['raw']['查询时间 UTC'], r'^\d{4}-\d{2}-\d{2}T.*\+00:00$')
        self.assertEqual(query.call_args.kwargs['region'], 'JP')
        self.assertIsInstance(query.call_args.kwargs['cancel'], bridge._Cancellation)

    def test_java_cancel_checked_before_and_after_non_cancellable_service(self):
        with patch.object(bridge, 'query') as query:
            result = json.loads(bridge.run_query('本机公网 IP', '', cancel=JavaBoolean(True)))
            self.assertTrue(result['cancelled'])
            self.assertEqual(result['error']['code'], 'cancelled')
            query.assert_not_called()
        flag = JavaBoolean()

        def finish_late(*args, **kwargs):
            flag.value = True
            return {'公网 IP': '8.8.8.8'}

        with patch.object(bridge, 'query', side_effect=finish_late):
            result = json.loads(bridge.run_query('本机公网 IP', '', cancel=flag))
        self.assertFalse(result['ok'])
        self.assertEqual(result['raw'], {})
        self.assertTrue(result['cancelled'])
        self.assertTrue(bridge._Cancellation(threading.Event()).is_set() is False)

    def test_cancel_exception_and_provider_codes_are_localized(self):
        with patch.object(bridge, 'query', side_effect=QueryCancelled):
            data = json.loads(bridge.run_query('域名档案', 'python.org', language='ja'))
        self.assertTrue(data['cancelled'])
        self.assertEqual(data['error']['message'], bridge.UI['ja']['cancelled'])
        with patch.object(bridge, 'query', side_effect=PublicQueryError('invalid_domain')):
            data = json.loads(bridge.run_query('域名档案', 'localhost', language='es'))
        self.assertEqual(data['error']['message'], bridge.UI['es']['invalid_domain'])
        with patch.object(bridge, 'query', side_effect=RuntimeError('private filesystem detail')):
            encoded = bridge.run_query('域名档案', 'python.org', language='en')
        self.assertNotIn('private filesystem', encoded)
        self.assertEqual(json.loads(encoded)['error']['code'], 'network_error')

    def test_invalid_module_or_input_never_reaches_query(self):
        cases = [('unknown', '8.8.8.8'), ('域名档案', ''), ('号码归属地', 'x' * 5001)]
        with patch.object(bridge, 'query') as query:
            for kind, value in cases:
                self.assertFalse(json.loads(bridge.run_query(kind, value))['ok'])
            self.assertFalse(json.loads(bridge.run_query('国内平台', '2', platform='Unsupported'))['ok'])
            query.assert_not_called()

    def test_offline_phone_and_username_tools_use_real_shared_services(self):
        phone = json.loads(bridge.run_query('号码归属地', '+12025550123', language='en'))
        self.assertTrue(phone['ok'])
        self.assertEqual(phone['raw']['国家呼叫码'], 1)
        self.assertEqual(phone['result']['Country calling code'], '1')
        self.assertIn('does not identify a person', phone['result']['Notes'])
        username = json.loads(bridge.run_query('用户名链接', 'example', language='es'))
        self.assertEqual(username['result']['GitHub'], 'https://github.com/example')
        self.assertIn('sin verificar', username['result']['Notas'])

    def test_reports_preserve_unicode_and_escape_active_content(self):
        result = {'说明': '日本語、Español、中文', '=unsafe-key': '   =HYPERLINK("https://x")',
                  '<script>': '<img src=x onerror=alert(1)>', 'multiline': 'a\nb'}
        envelope = json.dumps({'ok': True, 'result': result}, ensure_ascii=False)
        self.assertEqual(json.loads(bridge.render_report(envelope, 'json')), result)
        html_report = bridge.render_report(envelope, 'html')
        self.assertNotIn('<script>', html_report)
        self.assertNotIn('<img src=', html_report)
        self.assertIn('&lt;script&gt;', html_report)
        self.assertIn('Android report', html_report)
        csv_report = bridge.render_report(envelope, '.CSV')
        self.assertTrue(csv_report.startswith('\ufeff'))
        rows = list(csv.reader(io.StringIO(csv_report.removeprefix('\ufeff'))))
        self.assertEqual(rows[2], ["'=unsafe-key", "'   =HYPERLINK(\"https://x\")"])
        self.assertEqual(rows[-1], ['multiline', 'a\nb'])

    def test_reports_reject_failures_and_non_mapping_results(self):
        for value in ('[]', '{"ok":false,"result":{}}'):
            with self.assertRaises(ValueError):
                bridge.render_report(value, 'json')
        with self.assertRaises(ValueError):
            bridge.render_report('{}', 'exe')


if __name__ == '__main__':
    unittest.main()
