"""Regression coverage for loopback boundaries and public query adaptation."""
import http.client
import json
import threading
import unittest
from unittest.mock import patch

from web_console import start_console, run_lookup


class WebQueryTests(unittest.TestCase):
    def test_independent_source_errors_preserve_available_domain_data(self):
        with patch('web_console.registration', return_value={'域名': 'example.com', '到期时间': '2030-01-01'}), \
                patch('web_console.dns_records', side_effect=RuntimeError('private diagnostic')), \
                patch('web_console.website_info', return_value={'HTTP 状态': 200, '证书剩余天数': 14}):
            report = run_lookup({'tool': 'overview', 'target': 'EXAMPLE.COM'})
        self.assertEqual(report['target'], 'example.com')
        self.assertEqual(report['sources'][0]['fields']['Expires'], '2030-01-01')
        self.assertEqual(report['sources'][1]['status'], 'error')
        self.assertEqual(report['sources'][2]['fields']['Certificate days remaining'], 14)
        self.assertNotIn('private diagnostic', json.dumps(report))

    def test_offline_services_use_existing_engine(self):
        report = run_lookup({'tool': 'phone', 'target': '+12025550123', 'region': 'US'})
        self.assertEqual(report['sources'][0]['status'], 'ok')
        self.assertEqual(report['sources'][0]['fields']['E.164 format'], '+12025550123')

    def test_invalid_tool_and_private_domain_do_not_start_queries(self):
        with self.assertRaises(ValueError):
            run_lookup({'tool': '__import__', 'target': 'example.com'})
        with self.assertRaises(ValueError):
            run_lookup({'tool': 'overview', 'target': 'localhost'})
        with self.assertRaises(ValueError):
            run_lookup({'tool': 'phone', 'target': 'a', 'region': 'invalid'})

    def test_login_and_generic_profile_pages_remain_partial_not_verified(self):
        for page_status in ('需要登录或验证；账号状态未知', '返回平台通用页面，未取得用户资料'):
            with patch('web_console.query', return_value={'HTTP 状态': 200, '页面状态': page_status}):
                report = run_lookup({'tool': 'domestic', 'target': 'https://space.bilibili.com/2'})
            self.assertEqual(report['sources'][0]['status'], 'partial')
            self.assertEqual(report['sources'][0]['fields']['HTTP status'], 200)

    def test_cancelled_sources_are_not_recorded_as_success(self):
        event = threading.Event()
        event.set()
        report = run_lookup({'tool': 'github', 'target': 'octocat'}, event)
        self.assertEqual(report['sources'][0]['status'], 'cancelled')


class WebBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = start_console(port=0, open_browser=False)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def headers(self):
        return {'Origin': self.server.origin, 'X-GhostTrack-Token': self.server.token, 'Content-Type': 'application/json'}

    def test_assets_are_allowlisted_and_metadata_omits_local_files(self):
        status, headers, _ = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        for path in ('/../archive.json', '/state.json', '/.git/config', '/web_console.py'):
            self.assertEqual(self.request('GET', path)[0], 404)
        status, _, body = self.request('GET', '/api/meta')
        data = json.loads(body)
        self.assertEqual(data['runtime'], 'local')
        self.assertIn('website', data['tools'])
        self.assertEqual(data['token'], self.server.token)

    def test_host_origin_and_session_token_are_all_required(self):
        body = json.dumps({'id': 'origin-test', 'tool': 'phone', 'target': '+12025550123'})
        for headers in ({}, {**self.headers(), 'Origin': 'https://untrusted.example'},
                        {**self.headers(), 'X-GhostTrack-Token': 'bad'},
                        {**self.headers(), 'Host': 'attacker.example'}):
            self.assertEqual(self.request('POST', '/api/query', body, headers)[0], 403)
        self.assertEqual(self.request('GET', '/', headers={'Host': 'attacker.example'})[0], 403)

    def test_authenticated_post_and_body_bounds(self):
        payload = {'id': 'phone-test', 'tool': 'phone', 'target': '+12025550123'}
        status, _, body = self.request('POST', '/api/query', json.dumps(payload), self.headers())
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['sources'][0]['status'], 'ok')
        self.assertEqual(self.request('POST', '/api/query', 'x' * 9000, self.headers())[0], 400)
        self.assertEqual(self.request('POST', '/api/query', '[]', self.headers())[0], 400)
        self.assertEqual(self.request('POST', '/api/query', '{}', {**self.headers(), 'Content-Type': 'text/plain'})[0], 415)

    def test_concurrency_limit_returns_retryable_response(self):
        self.server.slots.acquire()
        self.server.slots.acquire()
        try:
            status, headers, _ = self.request('POST', '/api/query', json.dumps({'id': 'slots-test', 'tool': 'phone', 'target': '+12025550123'}), self.headers())
            self.assertEqual(status, 429)
            self.assertIn('Retry-After', headers)
        finally:
            self.server.slots.release()
            self.server.slots.release()

    def test_cancellation_signals_only_the_matching_active_job(self):
        event = threading.Event()
        with self.server.lock:
            self.server.active['cancel-test'] = event
        try:
            status, _, body = self.request('POST', '/api/cancel', '{"id":"cancel-test"}', self.headers())
            self.assertEqual(status, 200)
            self.assertTrue(event.is_set())
            self.assertTrue(json.loads(body)['cancelled'])
        finally:
            self.server.active.pop('cancel-test', None)


if __name__ == '__main__':
    unittest.main()
