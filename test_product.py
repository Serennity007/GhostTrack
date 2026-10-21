import json
from pathlib import Path
import tempfile
import threading
import time
import tkinter as tk
import unittest
from unittest.mock import patch

from desktop import App
from reports import write_report
from storage import Store


class PersistenceTests(unittest.TestCase):
    def test_large_results_keep_persisted_state_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            store.settings['remember'] = True
            for value in ('old', 'new'):
                store.record('DNS 记录', value, 'CN', 'Auto', {'large': 'x' * 1_100_000})
            self.assertLess(store.path.stat().st_size, 2_000_000)
            loaded = Store(folder)
            self.assertFalse(loaded.warning)
            self.assertEqual(loaded.history[0]['input'], 'new')

    def test_history_is_session_only_by_default(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            store.record('国内平台', '123', 'CN', 'Bilibili', {'查询时间 UTC': '2026-10-21T00:00:00Z'})
            self.assertEqual(len(store.history), 1)
            self.assertEqual(Store(folder).history, [])

    def test_opt_in_bounded_persistence_and_clear(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            store.settings.update(remember=True, language='ja')
            for i in range(55):
                self.assertTrue(store.record('国内平台', str(i), 'CN', 'Bilibili', {'查询时间 UTC': str(i)}))
            loaded = Store(folder)
            self.assertEqual(len(loaded.history), 50)
            self.assertEqual(loaded.history[0]['input'], '54')
            self.assertEqual(loaded.settings['language'], 'ja')
            self.assertTrue(loaded.clear_history())
            self.assertEqual(Store(folder).history, [])

    def test_corrupt_and_unwritable_state_do_not_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / 'state.json').write_text('{bad', encoding='utf-8')
            store = Store(folder)
            self.assertTrue(store.warning)
            self.assertEqual(store.history, [])
            file = path / 'not-a-folder'
            file.write_text('file')
            self.assertFalse(Store(file).save())

    def test_report_escaping_and_spreadsheet_safety(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            data = {'name': '<script>alert(1)</script>', 'value': ' \t=1+1', 'other': '+123'}
            write_report(path / 'report.html', data)
            content = (path / 'report.html').read_text(encoding='utf-8')
            self.assertNotIn('<script>', content)
            self.assertIn('&lt;script&gt;', content)
            write_report(path / 'report.csv', data)
            self.assertIn("' \t=1+1", (path / 'report.csv').read_text(encoding='utf-8-sig'))
            write_report(path / 'report.json', data)
            self.assertEqual(json.loads((path / 'report.json').read_text()), data)


class WorkflowTests(unittest.TestCase):
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

    def test_cancelled_late_response_cannot_replace_new_result(self):
        started, finish, returned = threading.Event(), threading.Event(), threading.Event()
        def pending(*args, **kwargs):
            started.set()
            finish.wait(2)
            returned.set()
            return {'IP': '8.8.8.8'}
        with patch('desktop.query', side_effect=pending):
            self.app.value.set('8.8.8.8')
            self.app.start()
            self.assertTrue(started.wait(1))
            old_id = self.app.job_id
            self.app.cancel()
            self.app.result = {'IP': 'new-result'}
            finish.set()
            self.assertTrue(returned.wait(1))
            self.app.events.put((old_id, True, {'IP': 'stale'}, None))
            self.app.poll()
            self.assertEqual(self.app.result['IP'], 'new-result')
            self.assertEqual(self.app.store.history, [])

    def test_worker_context_history_filter_and_copy(self):
        with patch('desktop.query', return_value={'IP': '8.8.8.8', '国家': 'Example'}):
            self.app.value.set('8.8.8.8')
            self.app.start()
            deadline = time.monotonic() + 2
            while self.app.busy and time.monotonic() < deadline:
                self.app.poll()
                self.root.update_idletasks()
                time.sleep(.01)
            self.assertFalse(self.app.busy)
            self.assertEqual(self.app.result['查询输入'], '8.8.8.8')
            self.assertEqual(len(self.app.store.history), 1)
            self.app.filter.set('Example')
            rows = self.app.tree.get_children()
            self.assertEqual(len(rows), 1)
            self.app.tree.selection_set(rows[0])
            self.app.copy_selected()
            self.assertEqual(self.root.clipboard_get(), 'Example')
            self.app.copy()
            self.assertIn('8.8.8.8', self.root.clipboard_get())

    def test_paste_auto_detects_platform(self):
        self.app.select(4)
        self.root.clipboard_clear()
        self.root.clipboard_append('分享 https://www.xiaohongshu.com/user/profile/1234567890abcdef12345678 打开APP')
        self.app.paste()
        self.assertEqual(self.app.platform.get(), 'Xiaohongshu')


if __name__ == '__main__':
    unittest.main()
