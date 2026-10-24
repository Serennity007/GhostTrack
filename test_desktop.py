import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from desktop import App, query
from i18n import UI, KEYS, LANGUAGES, localize


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.state_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.state_dir.cleanup()

    def test_actions_visible_at_minimum_window_size(self):
        root = tk.Tk()
        try:
            app = App(root, data_dir=self.state_dir.name)
            root.geometry('1000x700')
            root.update()
            for name in LANGUAGES:
                app.language.set(name)
                app.change_language()
                app.select(4)
                root.update()
                self.assertLessEqual(app.brand.winfo_reqwidth(), app.brand.master.winfo_width() - 40)
                for widget, key in app.bindings:
                    if key in ('copy_selected', 'copy', 'open_profile', 'export', 'history', 'settings', 'help'):
                        self.assertGreater(widget.winfo_width(), 20)
                        self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(),
                                             root.winfo_rootx() + root.winfo_width())
                        self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(),
                                             root.winfo_rooty() + root.winfo_height())
        finally:
            root.update_idletasks()
            root.destroy()

    def test_translations(self):
        for lang, strings in UI.items():
            self.assertEqual(set(strings), set(KEYS))
            self.assertTrue(all(strings.values()))
            self.assertIsInstance(localize(True, lang), str)
            self.assertEqual(localize(1.25, lang), 1.25)

    def test_atlas_reuses_owned_service_and_closes_it_with_desktop(self):
        from unittest.mock import MagicMock
        import threading
        root = tk.Tk()
        root.withdraw()
        service = MagicMock()
        service.origin = 'http://127.0.0.1:8765'
        service.lock = threading.Lock()
        event = threading.Event()
        service.active = {'test': event}
        try:
            app = App(root, data_dir=self.state_dir.name)
            with patch('desktop.start_console', return_value=service) as start, patch('desktop.webbrowser.open') as open_page:
                app.open_atlas()
                app.open_atlas()
                start.assert_called_once_with(port=8765, open_browser=False)
                self.assertEqual(open_page.call_count, 2)
                open_page.assert_called_with(service.origin)
                app.close()
            service.shutdown.assert_called_once()
            service.server_close.assert_called_once()
            self.assertTrue(event.is_set())
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass

    def test_atlas_port_conflict_does_not_open_an_unknown_service(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root, data_dir=self.state_dir.name)
            with patch('desktop.start_console', side_effect=OSError()), patch('desktop.webbrowser.open') as open_page, patch('desktop.messagebox.showerror') as error:
                app.open_atlas()
                open_page.assert_not_called()
                error.assert_called_once()
                self.assertIsNone(app.atlas_server)
        finally:
            root.destroy()

    def test_language_switch(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root, data_dir=self.state_dir.name)
            app.result = {'国家': 'Japan', '有效号码': True}
            for name, code in LANGUAGES.items():
                app.language.set(name)
                app.change_language()
                self.assertEqual(app.button['text'], UI[code]['run'])
                self.assertIn(localize('国家', code), app.localized_result())
                app.copy()
                self.assertIn(localize('国家', code), root.clipboard_get())
                for mode in range(len(app.MODES)):
                    app.select(mode)
                    root.update_idletasks()
                    self.assertEqual(app.entry['state'], 'disabled' if mode == 1 else 'normal')
                app.result = {'国家': 'Japan', '有效号码': True}
                app.show_result()
                app.tree.selection_set(app.tree.get_children()[0])
                app.copy_selected()
                self.assertEqual(root.clipboard_get(), 'Japan')
                app.result = {'主页链接': 'https://space.bilibili.com/123'}
                with patch('desktop.webbrowser.open') as open_page:
                    app.open_profile()
                    open_page.assert_called_once_with('https://space.bilibili.com/123')
                app.result = {'国家': 'Japan', '有效号码': True}
            app.events.put((app.job_id, False, 'input_error', None))
            app.poll()
            self.assertEqual(app.status.get(), UI['es']['failed'])
        finally:
            root.update_idletasks()
            root.destroy()

    def test_module_clear_examples_and_source_fields(self):
        root = tk.Tk(); root.withdraw()
        try:
            app = App(root, data_dir=self.state_dir.name)
            app.result = {'HTTPS / 页面标题': 'Example', 'RDAP / 失败原因': 'public_rate_limit'}
            app.lang = 'en'
            self.assertIn('HTTPS / Page title', app.localized_result())
            self.assertEqual(app.localized_result()['RDAP / Failure reason'], UI['en']['public_rate_limit'])
            app.result = {'名称服务器': 'ns1.example.com\nns2.example.com'}
            app.show_result()
            row = app.tree.get_children()[0]
            self.assertNotIn('\n', app.tree.item(row, 'values')[1])
            app.tree.selection_set(row)
            app.copy_selected()
            self.assertEqual(root.clipboard_get(), 'ns1.example.com\nns2.example.com')
            app.select(7)
            self.assertEqual(app.result, {})
            self.assertEqual(app.action_buttons[0]['state'], 'disabled')
            app.use_example()
            self.assertEqual(app.value.get(), 'https://www.python.org/')
            app.busy = True
            app.events.put((app.job_id, 'progress', {'completed': 1, 'total': 3, 'section': 'DNS'}, None))
            app.poll()
            self.assertTrue(app.busy)
            self.assertIn('DNS', app.status.get())
            self.assertEqual(app.result, {})
            app.cancel()
        finally:
            root.update_idletasks(); root.destroy()

    def test_phone(self):
        self.assertEqual(query('号码归属地', '+12025550123')['地区代码'], 'US')

    def test_private_ip(self):
        with self.assertRaises(ValueError):
            query('IP 归属地', '127.0.0.1')

    def test_ip(self):
        response = Mock()
        response.json.return_value = {'success': True, 'latitude': 1.25, 'longitude': 2.75}
        with patch('queries.requests.get', return_value=response) as get:
            self.assertEqual(query('IP 归属地', '8.8.8.8')['纬度'], 1.25)
            get.assert_called_once_with('https://ipwho.is/8.8.8.8', timeout=15)

    def test_service_failure(self):
        response = Mock()
        response.json.return_value = {'success': False, 'message': 'rate limit'}
        with patch('queries.requests.get', return_value=response):
            with self.assertRaisesRegex(ValueError, 'rate limit'):
                query('IP 归属地', '8.8.8.8')

    def test_username(self):
        self.assertIn('a%2Fb', query('用户名链接', 'a/b')['GitHub'])
        with self.assertRaises(ValueError):
            query('用户名链接', '')

    def test_exports_and_worker(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root, data_dir=self.state_dir.name)
            app.events.put((app.job_id, True, {'测试': '=1+1'}, None))
            app.poll()
            self.assertEqual(app.status.get(), '查询完成')
            with tempfile.TemporaryDirectory() as folder:
                for suffix in ('json', 'csv'):
                    target = Path(folder) / ('result.' + suffix)
                    with patch('desktop.filedialog.asksaveasfilename', return_value=str(target)):
                        app.export()
                    content = target.read_text(encoding='utf-8-sig')
                    if suffix == 'json':
                        self.assertEqual(json.loads(content), app.result)
                    else:
                        self.assertIn("'=1+1", content)
        finally:
            root.update_idletasks()
            root.destroy()


if __name__ == '__main__':
    unittest.main()
