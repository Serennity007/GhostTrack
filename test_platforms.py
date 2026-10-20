import unittest
from unittest.mock import MagicMock, patch

import requests

from platforms import lookup_profile, profile_url


class PlatformTests(unittest.TestCase):
    def response(self, code=200, body=b'<title>Example profile</title>', content_type='text/html'):
        response = MagicMock()
        response.status_code = code
        response.headers = {'Content-Type': content_type}
        response.encoding = 'utf-8'
        response.iter_content.return_value = [body]
        response.__enter__.return_value = response
        return response

    def test_profile_urls(self):
        for platform, value, url in (
                ('Bilibili', '123', 'https://space.bilibili.com/123'),
                ('Weibo', '123', 'https://weibo.com/u/123'),
                ('Zhihu', 'some-user', 'https://www.zhihu.com/people/some-user/'),
                ('Douban', 'some_user', 'https://www.douban.com/people/some_user/')):
            self.assertEqual(profile_url(platform, value), url)
            self.assertEqual(profile_url(platform, url), url)

    def test_invalid_profile_inputs(self):
        for value in ('nickname', '１２３', '123/other', 'https://space.bilibili.com.evil/123',
                      'https://space.bilibili.com@evil/123', 'http://space.bilibili.com/123',
                      'https://space.bilibili.com/123?x=y', 'https://space.bilibili.com:443/123'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                profile_url('Bilibili', value)

    def test_metadata(self):
        body = '<title>测试标题</title><meta name="description" content="公开 &amp; 简介">'.encode()
        with patch('platforms.requests.get', return_value=self.response(body=body)) as get:
            result = lookup_profile('Bilibili', '123')
            self.assertEqual(result['页面标题'], '测试标题')
            self.assertEqual(result['公开简介'], '公开 & 简介')
            self.assertIn('未核实', result['页面状态'])
            self.assertFalse(get.call_args.kwargs['allow_redirects'])
            self.assertTrue(get.call_args.kwargs['stream'])

    def test_restricted_and_missing(self):
        for code in (302, 403, 404, 412, 429, 500):
            with patch('platforms.requests.get', return_value=self.response(code)):
                result = lookup_profile('Weibo', '123')
                self.assertEqual(result['HTTP 状态'], code)
                self.assertNotIn('页面标题', result)
                self.assertIn('https://weibo.com/u/123', result.values())

    def test_login_gate(self):
        with patch('platforms.requests.get', return_value=self.response(body='<title>安全验证</title>'.encode())):
            self.assertIn('需要登录或验证', lookup_profile('Zhihu', 'user')['页面状态'])

    def test_network_failure_preserves_link(self):
        with patch('platforms.requests.get', side_effect=requests.Timeout):
            result = lookup_profile('Douban', 'user')
            self.assertEqual(result['主页链接'], 'https://www.douban.com/people/user/')
            self.assertIn('网络异常', result['页面状态'])

    def test_script_only_page(self):
        with patch('platforms.requests.get', return_value=self.response(body=b'<div id="app"></div>')):
            self.assertIn('脚本加载', lookup_profile('Bilibili', '123')['页面状态'])

    def test_non_html(self):
        with patch('platforms.requests.get', return_value=self.response(content_type='application/json')):
            self.assertIn('未返回可解析', lookup_profile('Bilibili', '123')['页面状态'])


if __name__ == '__main__':
    unittest.main()
