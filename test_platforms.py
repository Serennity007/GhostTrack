import unittest
from unittest.mock import MagicMock, patch

import requests

from platforms import lookup_profile, profile_url, resolve_profile, detect_platform, ProfileInputError, QueryCancelled
import threading


class PlatformTests(unittest.TestCase):
    def test_new_platforms_and_share_text(self):
        for platform, identifier, prefix in (
                ('Douyin', 'MS4wLjABAAAA1234567890', 'https://www.douyin.com/user/'),
                ('Xiaohongshu', '1234567890abcdef12345678', 'https://www.xiaohongshu.com/user/profile/'),
                ('Kuaishou', 'example_user', 'https://www.kuaishou.com/profile/')):
            url = prefix + identifier
            self.assertEqual(profile_url(platform, identifier), url)
            self.assertEqual(detect_platform('分享主页 ' + url + '。 打开APP'), platform)
            self.assertEqual(resolve_profile('Bilibili', url), (platform, url))

    def test_xiaohongshu_sharing_token_and_alias(self):
        url = 'https://xiaohongshu.com/user/profile/1234567890abcdef12345678?xsec_token=public-share&tracking=ignore'
        self.assertEqual(profile_url('Xiaohongshu', url),
                         'https://www.xiaohongshu.com/user/profile/1234567890abcdef12345678?xsec_token=public-share')

    def test_short_link_resolution(self):
        response = self.response(302)
        response.headers['Location'] = 'https://www.douyin.com/user/MS4wLjABAAAA1234567890?source=share'
        with patch('platforms.requests.get', return_value=response) as get:
            platform, url = resolve_profile('Auto', '分享 http://v.douyin.com/abc123/ 打开APP')
            self.assertEqual(platform, 'Douyin')
            self.assertEqual(url, 'https://www.douyin.com/user/MS4wLjABAAAA1234567890')
            self.assertEqual(get.call_args.args[0], 'https://v.douyin.com/abc123/')

    def test_short_link_blocks_foreign_redirect(self):
        for target in ('https://127.0.0.1/private', 'https://evil.test/profile',
                       'https://www.douyin.com@evil.test/user/example'):
            response = self.response(302)
            response.headers['Location'] = target
            with patch('platforms.requests.get', return_value=response) as get:
                with self.assertRaises(ProfileInputError):
                    resolve_profile('Auto', 'https://v.douyin.com/abc123/')
                self.assertEqual(get.call_count, 1)

    def test_content_share_is_not_a_profile(self):
        with self.assertRaises(ProfileInputError):
            profile_url('Douyin', 'https://www.douyin.com/video/12345678')
        with self.assertRaises(ProfileInputError):
            profile_url('Xiaohongshu', 'https://www.xiaohongshu.com/explore/1234567890abcdef12345678')

    def test_short_link_fallback_preserves_link(self):
        with patch('platforms.requests.get', return_value=self.response(403)):
            result = lookup_profile('Auto', 'https://xhslink.com/abc123')
            self.assertEqual(result['主页链接'], 'https://xhslink.com/abc123')
            self.assertIn('访问受限', result['页面状态'])

    def test_cancelled_profile_does_not_request(self):
        cancel = threading.Event()
        cancel.set()
        with patch('platforms.requests.get') as get:
            with self.assertRaises(QueryCancelled):
                lookup_profile('Bilibili', '123', cancel)
            get.assert_not_called()

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
                      'https://space.bilibili.com:443/123'):
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

    def test_generic_platform_page_is_not_user_data(self):
        with patch('platforms.requests.get', return_value=self.response(body='<title>小红书 - 你的生活兴趣社区</title>'.encode())):
            result = lookup_profile('Xiaohongshu', '1234567890abcdef12345678')
            self.assertIn('未取得用户资料', result['页面状态'])
            self.assertNotIn('公开简介', result)

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
