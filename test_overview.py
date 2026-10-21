import gzip
import threading
import unittest
import zlib
from unittest.mock import patch
from public_data import decode_http_body, domain_overview, PublicQueryError
from platforms import QueryCancelled

class OverviewTests(unittest.TestCase):
    def test_bounded_compression_decoding(self):
        data = b'<title>Actual title</title>'
        for encoded, kind in ((gzip.compress(data), 'gzip'), (zlib.compress(data), 'deflate')):
            self.assertEqual(decode_http_body(encoded, kind), (data, 'content_parsed'))
        decoded, status = decode_http_body(gzip.compress(b'x' * 500000), 'gzip', 1000)
        self.assertEqual(len(decoded), 1000)
        self.assertEqual(status, 'content_truncated')
        self.assertEqual(decode_http_body(b'bad', 'gzip')[1], 'content_decode_failed')
        self.assertEqual(decode_http_body(b'bad', 'br')[1], 'content_unsupported')

    def test_partial_sources_and_progress(self):
        progress = []
        with patch('public_data.registration', side_effect=PublicQueryError('public_rate_limit')), \
             patch('public_data.dns_records', return_value={'DNS A': '8.8.8.8', '查询状态': '已完成'}), \
             patch('public_data.website_info', return_value={'页面标题': 'Example', '查询状态': '已完成'}):
            result = domain_overview('example.com', progress=progress.append)
        self.assertEqual(result['DNS / DNS A'], '8.8.8.8')
        self.assertEqual(result['HTTPS / 页面标题'], 'Example')
        self.assertEqual(result['RDAP / 失败原因'], 'public_rate_limit')
        self.assertEqual(result['查询状态'], '部分来源不可用')
        self.assertEqual(result['成功来源数'], 2)
        self.assertEqual(sorted(p['completed'] for p in progress), [1, 2, 3])
        self.assertEqual({p['section'] for p in progress}, {'RDAP', 'DNS', 'HTTPS'})

    def test_cancel_before_sources(self):
        cancel = threading.Event(); cancel.set()
        with patch('public_data.registration') as service:
            with self.assertRaises(QueryCancelled):
                domain_overview('example.com', cancel)
            service.assert_not_called()
