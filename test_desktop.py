import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from desktop import App, query


class DesktopTests(unittest.TestCase):
    def test_phone(self):
        self.assertEqual(query('号码归属地', '+12025550123')['地区代码'], 'US')

    def test_private_ip(self):
        with self.assertRaises(ValueError):
            query('IP 归属地', '127.0.0.1')

    def test_ip(self):
        response = Mock()
        response.json.return_value = {'success': True, 'latitude': 1.25, 'longitude': 2.75}
        with patch('desktop.requests.get', return_value=response) as get:
            self.assertEqual(query('IP 归属地', '8.8.8.8')['纬度'], 1.25)
            get.assert_called_once_with('https://ipwho.is/8.8.8.8', timeout=15)

    def test_service_failure(self):
        response = Mock()
        response.json.return_value = {'success': False, 'message': 'rate limit'}
        with patch('desktop.requests.get', return_value=response):
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
            app = App(root)
            app.events.put((True, {'测试': '=1+1'}))
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
            root.destroy()


if __name__ == '__main__':
    unittest.main()
