import socket
import ssl
import threading
import unittest
from unittest.mock import MagicMock, patch

import requests

from public_data import (PublicQueryError, PinnedHTTPS, api_json, dns_records,
                         domain_name, github_profile, public_addresses,
                         public_target, registration, website_info)
from platforms import QueryCancelled


class PublicDataTests(unittest.TestCase):
    def test_domain_normalization_and_validation(self):
        self.assertEqual(domain_name('https://Example.COM/path'), 'example.com')
        self.assertTrue(domain_name('例子.中国').startswith('xn--'))
        for value in ('localhost', '127.0.0.1', 'private.local', 'a..com', 'https://user:pass@example.com', '*.example.com'):
            with self.subTest(value=value), self.assertRaises(PublicQueryError):
                domain_name(value)

    def test_public_https_input(self):
        self.assertEqual(public_target('example.com')[1:], ('example.com', '/'))
        self.assertEqual(public_target('https://1.1.1.1/')[1], '1.1.1.1')
        self.assertEqual(public_target('https://[2606:4700:4700::1111]/')[1], '2606:4700:4700::1111')
        for value in ('http://example.com', 'https://example.com:8443/', 'https://user@example.com/', 'https://example.com/#part'):
            with self.assertRaises(PublicQueryError):
                public_target(value)
        for value in ('https://224.0.0.1/', 'https://[ff02::1]/', 'https://[::1]/'):
            with self.assertRaises(PublicQueryError):
                public_target(value)

    def test_mixed_public_private_dns_is_blocked(self):
        entries = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443)),
                   (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))]
        with patch('public_data.socket.getaddrinfo', return_value=entries):
            with self.assertRaises(PublicQueryError):
                public_addresses('example.com')

    def test_fake_ip_pool_uses_only_validated_public_doh_answer(self):
        entries = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('198.18.0.1', 443))]
        with patch('public_data.socket.getaddrinfo', return_value=entries):
            with patch('public_data.api_json', return_value=({'Answer': [{'type': 1, 'data': '8.8.8.8'}]}, 'source')):
                self.assertEqual(public_addresses('example.com'), ['8.8.8.8'])
            with patch('public_data.api_json', return_value=({'Answer': [{'type': 1, 'data': '127.0.0.1'}]}, 'source')):
                with self.assertRaises(PublicQueryError):
                    public_addresses('example.com')

    def test_pinned_connection_preserves_sni_and_verification(self):
        connection = PinnedHTTPS('example.com', '8.8.8.8')
        self.assertTrue(connection._context.check_hostname)
        self.assertEqual(connection._context.verify_mode, ssl.CERT_REQUIRED)
        connection._context = MagicMock()
        with patch('public_data.socket.create_connection') as connect:
            connection.connect()
            connect.assert_called_once_with(('8.8.8.8', 443), 8)
            connection._context.wrap_socket.assert_called_once_with(connect.return_value, server_hostname='example.com')

    def test_domain_registry_omits_registrant_contacts(self):
        data = {'ldhName': 'example.com', 'status': ['active'], 'nameservers': [{'ldhName': 'ns.example.net'}],
                'events': [{'eventAction': 'expiration', 'eventDate': '2030-01-01'}],
                'entities': [{'roles': ['registrant'], 'vcardArray': ['vcard', [['fn', {}, 'text', 'private person']]]},
                             {'roles': ['registrar'], 'vcardArray': ['vcard', [['fn', {}, 'text', 'Public Registrar']]]}]}
        with patch('public_data.api_json', return_value=(data, 'https://rdap.example.net/domain/example.com')):
            result = registration('example.com')
            self.assertEqual(result['注册商'], 'Public Registrar')
            self.assertEqual(result['到期时间'], '2030-01-01')
            self.assertNotIn('private person', str(result))

    def test_ip_registry_requires_global_address(self):
        with patch('public_data.api_json') as get:
            with self.assertRaises(PublicQueryError):
                registration('10.0.0.1', is_ip=True)
            get.assert_not_called()

    def test_asn_registration(self):
        data = {'name': 'EXAMPLE-NETWORK', 'startAutnum': 15169, 'endAutnum': 15169}
        with patch('public_data.api_json', return_value=(data, 'https://rdap.arin.net/registry/autnum/15169')) as get:
            result = registration('AS15169', is_ip=True)
            self.assertEqual(result['ASN'], 'AS15169')
            get.assert_called_once_with('https://rdap.org/autnum/15169', None)

    def test_dns_partial_results_survive_one_source_failure(self):
        def api(url, cancel):
            if 'type=MX' in url:
                raise requests.Timeout()
            return {'Status': 0, 'Answer': [{'name': 'example.com.', 'TTL': 60, 'data': 'public-value'}]}, url
        with patch('public_data.api_json', side_effect=api):
            result = dns_records('example.com')
            self.assertIn('public-value', result['DNS A'])
            self.assertEqual(result['DNS MX'], 'ERROR')
            self.assertEqual(result['查询状态'], '部分来源不可用')

    def test_large_dns_answers_are_explicitly_truncated(self):
        records = [{'name': 'example.com.', 'TTL': 1, 'data': 'x' * 1000}] * 30
        with patch('public_data.api_json', return_value=({'Status': 0, 'Answer': records}, 'source')):
            result = dns_records('example.com')
            self.assertLess(len(result['DNS TXT']), 6100)
            self.assertIn('TRUNCATED', result['DNS TXT'])
            self.assertIn('TXT', result['截断记录类型'])

    def test_github_partial_profile_avoids_contact_fields(self):
        data = {'login': 'octocat', 'name': 'Example', 'email': 'not-exported@example.com', 'public_repos': 8}
        with patch('public_data.api_json', side_effect=[(data, 'https://api.github.com/users/octocat'), requests.Timeout()]):
            result = github_profile('https://github.com/octocat')
            self.assertEqual(result['公开仓库数'], 8)
            self.assertEqual(result['查询状态'], '部分来源不可用')
            self.assertNotIn('not-exported@example.com', str(result))

    def test_github_input_rejects_repository_url(self):
        with self.assertRaises(PublicQueryError):
            github_profile('https://github.com/owner/repo')

    def fake_connection(self, status=200, location=None):
        connection = MagicMock()
        connection.sock.getpeercert.return_value = {
            'issuer': ((('organizationName', 'Example CA'),),),
            'notBefore': 'Jan  1 00:00:00 2020 GMT', 'notAfter': 'Jan  1 00:00:00 2030 GMT',
            'subjectAltName': (('DNS', 'example.com'),)}
        response = connection.getresponse.return_value
        response.status = status
        response.getheader.side_effect = lambda key, default=None: {
            'Content-Type': 'text/html; charset=utf-8', 'Location': location}.get(key, default)
        response.read.side_effect = [b'<title>Example page</title>', b'']
        return connection

    def test_website_and_certificate(self):
        connection = self.fake_connection()
        with patch('public_data.public_addresses', return_value=['8.8.8.8']), patch('public_data.PinnedHTTPS', return_value=connection):
            result = website_info('https://example.com/')
            self.assertEqual(result['页面标题'], 'Example page')
            self.assertEqual(result['证书颁发者'], 'Example CA')
            self.assertEqual(result['证书覆盖域名'], 'example.com')
            self.assertEqual(result['HTTP 状态'], 200)
            connection.close.assert_called_once()

    def test_compressed_website_title(self):
        import gzip
        connection = self.fake_connection()
        response = connection.getresponse.return_value
        response.getheader.side_effect = lambda key, default=None: {
            'Content-Type': 'text/html; charset=utf-8', 'Content-Encoding': 'gzip'}.get(key, default)
        response.read.side_effect = [gzip.compress(b'<title>Compressed title</title>'), b'']
        with patch('public_data.public_addresses', return_value=['8.8.8.8']), patch('public_data.PinnedHTTPS', return_value=connection):
            result = website_info('https://example.com/')
            self.assertEqual(result['页面标题'], 'Compressed title')
            self.assertEqual(result['页面内容状态'], 'content_parsed')

    def test_website_blocks_redirect_to_private_network(self):
        connection = self.fake_connection(302, 'https://127.0.0.1/')
        with patch('public_data.public_addresses', return_value=['8.8.8.8']), patch('public_data.PinnedHTTPS', return_value=connection) as factory:
            with self.assertRaises(PublicQueryError):
                website_info('https://example.com/')
            self.assertEqual(factory.call_count, 1)

    def test_cancelled_api_has_no_network_request(self):
        cancel = threading.Event()
        cancel.set()
        with patch('public_data.requests.get') as get:
            with self.assertRaises(QueryCancelled):
                api_json('https://dns.google/resolve', cancel)
            get.assert_not_called()


if __name__ == '__main__':
    unittest.main()
