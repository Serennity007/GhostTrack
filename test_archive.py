import json
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path

from archive import LIMIT, Archive, ArchiveError, flatten, normalize_phone
from desktop import App
from i18n import UI
from queries import query


class ArchiveUnitTests(unittest.TestCase):
    def test_normalize_phone_requires_valid_number(self):
        e164, display = normalize_phone('+86 138 0013 8000')
        self.assertEqual(e164, '+8613800138000')
        self.assertIn('138', display)
        for bad in ('', 'abc', '+86123', '12345'):
            with self.assertRaises(ArchiveError) as ctx:
                normalize_phone(bad)
            self.assertEqual(ctx.exception.code, 'archive_phone')

    def test_add_validates_platform_url_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Archive(folder)
            with self.assertRaises(ArchiveError) as ctx:
                archive.add('+8613800138000', 'Bilibili', 'https://example.com/user/2')
            self.assertEqual(ctx.exception.code, 'archive_url')
            with self.assertRaises(ArchiveError) as ctx:
                archive.add('+8613800138000', 'NotAPlatform', 'https://space.bilibili.com/2')
            self.assertEqual(ctx.exception.code, 'archive_platform')
            with self.assertRaises(ArchiveError) as ctx:
                archive.add('+8613800138000', 'Bilibili', 'https://space.bilibili.com/2', source='guessed')
            self.assertEqual(ctx.exception.code, 'archive_source')
            with self.assertRaises(ArchiveError):
                archive.add('+8613800138000', 'Weibo', 'https://space.bilibili.com/2')

    def test_add_dedupe_persist_remove_and_cap(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Archive(folder)
            item, created, saved = archive.add('+8613800138000', 'Bilibili', 'https://space.bilibili.com/2',
                                               source='self', note='mine')
            self.assertTrue(created and saved)
            again, created, _ = archive.add('13800138000', 'Bilibili', 'https://space.bilibili.com/2',
                                            region='CN', source='public', note='updated')
            self.assertFalse(created)
            self.assertEqual(again['id'], item['id'])
            self.assertEqual(len(archive.records), 1)
            loaded = Archive(folder)
            self.assertEqual(loaded.records[0]['source'], 'public')
            self.assertEqual(loaded.records[0]['note'], 'updated')
            self.assertEqual(loaded.records[0]['phone'], '+8613800138000')
            for index in range(LIMIT + 5):
                archive.add(f'+86138{index:08d}', 'Zhihu', f'https://www.zhihu.com/people/u{index:04d}')
            self.assertEqual(len(Archive(folder).records), LIMIT)
            self.assertFalse(archive.remove('missing'))
            self.assertTrue(archive.remove(archive.records[0]['id']))
            self.assertEqual(len(Archive(folder).records), LIMIT - 1)

    def test_search_by_digits_keyword_and_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Archive(folder)
            archive.add('+8613800138000', 'Bilibili', 'https://space.bilibili.com/2', note='主号')
            archive.add('+12025550123', 'Zhihu', 'https://www.zhihu.com/people/octo', source='public')
            self.assertEqual(len(archive.search('')), 2)
            self.assertEqual(len(archive.search('13800138000')), 1)
            self.assertEqual(archive.search('13800138000')[0]['platform'], 'Bilibili')
            self.assertEqual(len(archive.search('+1 202')), 1)
            self.assertEqual(len(archive.search('主号')), 1)
            self.assertEqual(len(archive.search('zhihu')), 1)
            self.assertEqual(archive.search('+86999'), [])

    def test_corrupt_and_oversize_archive_do_not_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'archive.json'
            path.write_text('{bad', encoding='utf-8')
            archive = Archive(folder)
            self.assertTrue(archive.warning)
            self.assertEqual(archive.records, [])
            path.write_text(json.dumps({'records': [{'id': 1}, {'id': 'x', 'phone': '+1', 'phone_display': '+1',
                                                     'platform': 'Bilibili', 'url': 'u', 'source': 'self',
                                                     'note': '', 'added': 't'}]}), encoding='utf-8')
            self.assertEqual(len(Archive(folder).records), 1)

    def test_flatten_uses_localizable_namespace(self):
        records = [{'platform': 'Bilibili', 'phone_display': '+86 138 0013 8000',
                    'url': 'https://space.bilibili.com/2', 'source': 'self',
                    'note': 'n', 'added': '2026-10-21T00:00:00+00:00', 'id': 'x', 'phone': '+8613800138000'}]
        data = flatten(records)
        self.assertIn('Archive 01 / 平台', data)
        self.assertEqual(data['Archive 01 / 来源'], '本人授权提供')


class ArchiveQueryTests(unittest.TestCase):
    def test_query_formats_matches_and_bounds_display(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Archive(folder)
            result = query('授权账号档案', 'anything', archive=archive)
            self.assertEqual(result['匹配记录数'], 0)
            self.assertIn('提示', result)
            for index in range(15):
                archive.add(f'+86138001{index:05d}', 'Bilibili', f'https://space.bilibili.com/{index + 1}')
            result = query('授权账号档案', '', archive=archive)
            self.assertEqual(result['匹配记录数'], 15)
            self.assertEqual(result['显示记录数'], 12)
            self.assertIn('Archive 12 / 平台', result)
            self.assertNotIn('Archive 13 / 平台', result)
            self.assertEqual(len(result), 3 + 12 * 5 + 1)
            result = query('授权账号档案', '+8613800100003', archive=archive)
            self.assertEqual(result['匹配记录数'], 1)
            with self.assertRaises(ValueError):
                query('授权账号档案', 'x', archive=None)


class ArchiveWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = App(self.root, self.directory.name)
        self.root.update_idletasks()

    def tearDown(self):
        self.root.update_idletasks()
        self.app.close()
        self.directory.cleanup()

    def pump(self):
        deadline = time.monotonic() + 2
        while self.app.busy and time.monotonic() < deadline:
            self.app.poll()
            self.root.update_idletasks()
            time.sleep(.01)

    def test_save_from_result_then_search_by_phone(self):
        self.app.result = {'平台': 'Bilibili', '主页链接': 'https://space.bilibili.com/2'}
        self.app.update_actions()
        self.assertEqual(self.app.action_buttons[4]['state'], 'normal')
        item, created, saved = self.app.archive.add('+8613800138000', 'Bilibili',
                                                    'https://space.bilibili.com/2', note='本人')
        self.assertTrue(created and saved)
        self.app.select(11)
        self.assertEqual(self.app.hint.cget('text'), UI[self.app.lang]['hint_archive'])
        self.app.value.set('13800138000')
        self.app.start()
        self.pump()
        self.assertFalse(self.app.busy)
        self.assertEqual(self.app.result['匹配记录数'], 1)
        self.assertEqual(self.app.result['Archive 01 / 主页'], 'https://space.bilibili.com/2')
        self.assertEqual(len(self.app.store.history), 1)
        self.app.lang = 'en'
        localized = self.app.localized_result()
        self.assertIn('Archive 01 / Platform', localized)
        self.assertIn('Matching records', localized)
        self.assertEqual(localized['Archive 01 / Source'], 'Provided by the owner')

    def test_save_button_disabled_without_profile_result(self):
        self.app.result = {'国家': 'Japan'}
        self.app.update_actions()
        self.assertEqual(self.app.action_buttons[4]['state'], 'disabled')
        self.app.save_archive()
        self.assertEqual(self.app.status.get(), UI[self.app.lang]['no_profile'])

    def test_archive_persists_across_app_sessions(self):
        self.app.archive.add('+8613800138000', 'Douyin', 'https://www.douyin.com/user/MS4wLjABAAAA')
        loaded = Archive(self.directory.name)
        self.assertEqual(len(loaded.records), 1)
        self.assertEqual(loaded.records[0]['platform'], 'Douyin')


if __name__ == '__main__':
    unittest.main()
