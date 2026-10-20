"""Windows desktop edition of HunxByts/GhostTrack."""
import csv
import ipaddress
import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import quote

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests

VERSION = '1.0.0'


def query(kind, value, region='CN'):
    value = value.strip()
    if kind == '号码归属地':
        number = phonenumbers.parse(value, region)
        return {'国际格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                '归属地': geocoder.description_for_number(number, 'zh'),
                '运营商': carrier.name_for_number(number, 'zh'),
                '地区代码': phonenumbers.region_code_for_number(number),
                '时区': ', '.join(timezone.time_zones_for_number(number)),
                '有效号码': phonenumbers.is_valid_number(number),
                '说明': '号码段元数据，不代表持有人身份或实时位置'}
    if kind == '用户名链接':
        if not value or len(value) > 100 or any(c.isspace() for c in value):
            raise ValueError('请输入不含空白的用户名（1–100 字符）')
        name = quote(value, safe='')
        return {'GitHub': f'https://github.com/{name}',
                'Instagram': f'https://www.instagram.com/{name}/',
                'X': f'https://x.com/{name}',
                '说明': '仅生成公开主页链接；未核实账号存在或身份归属'}
    if kind == '本机公网 IP':
        response = requests.get('https://api.ipify.org', timeout=15)
        response.raise_for_status()
        return {'公网 IP': str(ipaddress.ip_address(response.text.strip()))}
    address = ipaddress.ip_address(value)
    if not address.is_global:
        raise ValueError('请输入公网 IPv4 或 IPv6 地址，内网地址没有公网归属地')
    response = requests.get(f'https://ipwho.is/{address}', timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data.get('success'):
        raise ValueError(data.get('message', '服务未返回有效结果'))
    return {'IP': str(address), '国家': data.get('country'), '地区': data.get('region'),
            '城市': data.get('city'), '纬度': data.get('latitude'), '经度': data.get('longitude'),
            '网络服务商': data.get('connection', {}).get('isp'),
            '说明': 'IP 数据库估算位置，不代表设备实时位置'}


class App:
    def __init__(self, root):
        self.root, self.result = root, {}
        self.events = queue.Queue()
        root.title(f'GhostTrack 中文版 {VERSION}')
        root.geometry('820x600')
        root.minsize(650, 450)
        panel = ttk.Frame(root, padding=20)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='GhostTrack 信息查询', font=('Microsoft YaHei UI', 20)).pack(anchor='w')
        ttk.Label(panel, text='基于 HunxByts/GhostTrack · IP 归属地 / 号码元数据 / 公开主页链接').pack(anchor='w', pady=(4, 18))
        self.kind = tk.StringVar(value='IP 归属地')
        ttk.Combobox(panel, textvariable=self.kind, state='readonly',
                     values=['IP 归属地', '本机公网 IP', '号码归属地', '用户名链接']).pack(fill='x')
        self.value = tk.StringVar()
        entry = ttk.Entry(panel, textvariable=self.value)
        entry.pack(fill='x', pady=10)
        entry.bind('<Return>', lambda _: self.start())
        ttk.Label(panel, text='输入 IP、带国家代码的号码（如 +86…）或用户名；本机公网 IP 无需输入。').pack(anchor='w')
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=10)
        ttk.Label(row, text='无国际区号时使用地区：').pack(side='left')
        self.region = tk.StringVar(value='CN')
        ttk.Combobox(row, textvariable=self.region, values=sorted(phonenumbers.SUPPORTED_REGIONS),
                     state='readonly', width=6).pack(side='left')
        self.button = ttk.Button(row, text='开始查询', command=self.start)
        self.button.pack(side='right')
        self.status = tk.StringVar(value='就绪')
        ttk.Label(panel, textvariable=self.status).pack(anchor='w')
        self.output = tk.Text(panel, wrap='word', font=('Microsoft YaHei UI', 11), state='disabled')
        self.output.pack(fill='both', expand=True, pady=8)
        actions = ttk.Frame(panel)
        actions.pack(fill='x')
        ttk.Button(actions, text='复制结果', command=self.copy).pack(side='left')
        ttk.Button(actions, text='导出 JSON / CSV', command=self.export).pack(side='right')
        root.after(100, self.poll)

    def start(self):
        if str(self.button['state']) == 'disabled':
            return
        args = self.kind.get(), self.value.get(), self.region.get()
        self.button.config(state='disabled')
        self.status.set('查询中…')
        self.result = {}
        self.render('')
        def work():
            try:
                self.events.put((True, query(*args)))
            except Exception as error:
                self.events.put((False, str(error)))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            success, data = self.events.get_nowait()
            self.button.config(state='normal')
            if success:
                self.result = data
                self.render('\n\n'.join(f'{k}：{v}' for k, v in data.items()))
                self.status.set('查询完成')
            else:
                self.status.set('查询失败，请检查输入或网络后重试')
                self.render(f'错误：{data}')
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def render(self, text):
        self.output.config(state='normal')
        self.output.delete('1.0', 'end')
        self.output.insert('1.0', text)
        self.output.config(state='disabled')

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output.get('1.0', 'end-1c'))

    def export(self):
        if not self.result:
            messagebox.showinfo('提示', '请先完成查询')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json',
                   filetypes=[('JSON', '*.json'), ('CSV', '*.csv')])
        if not path:
            return
        try:
            if path.lower().endswith('.csv'):
                with open(path, 'w', encoding='utf-8-sig', newline='') as stream:
                    writer = csv.writer(stream)
                    writer.writerow(['字段', '值'])
                    for key, value in self.result.items():
                        value = str(value)
                        writer.writerow([key, "'" + value if value.startswith(('=', '+', '-', '@')) else value])
            else:
                with open(path, 'w', encoding='utf-8') as stream:
                    json.dump(self.result, stream, ensure_ascii=False, indent=2)
            self.status.set('导出完成')
        except OSError as error:
            messagebox.showerror('导出失败', str(error))


if __name__ == '__main__':
    window = tk.Tk()
    App(window)
    window.mainloop()
