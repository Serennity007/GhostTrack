"""Windows desktop edition of HunxByts/GhostTrack."""
import csv
import ipaddress
import json
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import quote

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from platforms import PLATFORMS, lookup_profile

VERSION = '1.2.0'


def query(kind, value, region='CN', language='zh', platform='Bilibili'):
    value = value.strip()
    if kind == '国内平台':
        return lookup_profile(platform, value)
    if kind == '号码归属地':
        number = phonenumbers.parse(value, region)
        return {'国际格式': phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                '归属地': geocoder.description_for_number(number, language),
                '运营商': carrier.name_for_number(number, language),
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


from i18n import LANGUAGES, UI, localize


class App:
    BG, PANEL, CARD = '#0b1020', '#11192d', '#18233b'
    FG, MUTED, ACCENT = '#edf3ff', '#a6b5d2', '#5ee0bc'
    MODES = ['IP 归属地', '本机公网 IP', '号码归属地', '用户名链接', '国内平台']
    MODE_KEYS = ['ip', 'self', 'phone', 'username', 'domestic']

    def __init__(self, root):
        self.root, self.result = root, {}
        self.events = queue.Queue()
        self.lang, self.mode, self.busy = 'zh', 0, False
        self.state = 'ready'
        self.value = tk.StringVar()
        self.region = tk.StringVar(value='CN')
        self.platform = tk.StringVar(value='Bilibili')
        self.language = tk.StringVar(value='简体中文')
        self.status = tk.StringVar()
        self.bindings = []
        root.title(f'GhostTrack / {VERSION}')
        root.geometry('1100x760')
        root.minsize(1000, 700)
        root.configure(bg=self.BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=self.CARD, background=self.CARD,
                        foreground=self.FG, arrowcolor=self.ACCENT, padding=7)
        style.map('TCombobox', fieldbackground=[('readonly', self.CARD)],
                  foreground=[('readonly', self.FG)], selectbackground=[('readonly', self.CARD)])
        style.configure('Result.Treeview', background=self.PANEL, fieldbackground=self.PANEL,
                        foreground=self.FG, rowheight=44, borderwidth=0, font=('Microsoft YaHei UI', 10))
        style.configure('Result.Treeview.Heading', background=self.CARD, foreground=self.MUTED,
                        padding=12, font=('Microsoft YaHei UI', 10))
        style.map('Result.Treeview', background=[('selected', '#245565')])
        side = tk.Frame(root, bg=self.PANEL, width=245)
        side.pack(side='left', fill='y')
        side.pack_propagate(False)
        tk.Label(side, text='GHOST / TRACK', bg=self.PANEL, fg=self.ACCENT,
                 font=('Segoe UI', 19, 'bold')).pack(anchor='w', padx=22, pady=(35, 4))
        tk.Label(side, text=f'DESKTOP EDITION   /   {VERSION}', bg=self.PANEL,
                 fg=self.MUTED, font=('Segoe UI', 9)).pack(anchor='w', padx=22, pady=(0, 42))
        self.label(side, 'tools', bg=self.PANEL).pack(anchor='w', padx=22, pady=(0, 12))
        self.nav = []
        for index, key in enumerate(self.MODE_KEYS):
            button = self.button_widget(side, key, lambda n=index: self.select(n))
            button.pack(fill='x', padx=14, pady=5)
            self.nav.append(button)
        footer = tk.Frame(side, bg=self.PANEL)
        footer.pack(side='bottom', fill='x', padx=22, pady=25)
        self.label(footer, 'privacy', bg=self.PANEL, wraplength=200).pack(anchor='w', pady=8)
        tk.Label(footer, text='Built on HunxByts/GhostTrack', bg=self.PANEL,
                 fg=self.MUTED, font=('Segoe UI', 8)).pack(anchor='w')
        main = tk.Frame(root, bg=self.BG)
        main.pack(side='left', fill='both', expand=True, padx=30, pady=28)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(4, weight=1)
        top = tk.Frame(main, bg=self.BG)
        top.grid(row=0, column=0, sticky='ew')
        self.label(top, 'workspace', size=11).pack(side='left')
        language = ttk.Combobox(top, textvariable=self.language, values=list(LANGUAGES),
                                state='readonly', width=15)
        language.pack(side='right')
        language.bind('<<ComboboxSelected>>', self.change_language)
        self.heading = self.label(main, 'tagline', size=23, color=self.FG, wraplength=730)
        self.heading.grid(row=1, column=0, sticky='w', pady=(20, 24))
        form = tk.Frame(main, bg=self.PANEL, padx=22, pady=18)
        form.grid(row=2, column=0, sticky='ew')
        self.label(form, 'parameters', bg=self.PANEL, color=self.ACCENT).pack(anchor='w')
        self.label(form, 'input', bg=self.PANEL).pack(anchor='w', pady=(14, 6))
        self.entry = tk.Entry(form, textvariable=self.value, bg=self.CARD, fg=self.FG,
                              insertbackground=self.ACCENT, relief='flat', font=('Segoe UI', 14))
        self.entry.pack(fill='x', ipady=10)
        self.entry.bind('<Return>', lambda _: self.start())
        self.hint = tk.Label(form, bg=self.PANEL, fg=self.MUTED,
                             font=('Microsoft YaHei UI', 9), anchor='w', wraplength=680)
        self.hint.pack(fill='x', pady=10)
        row = tk.Frame(form, bg=self.PANEL)
        row.pack(fill='x')
        self.region_label = self.label(row, 'region', bg=self.PANEL)
        self.region_label.pack(side='left', padx=(0, 8))
        self.region_box = ttk.Combobox(row, textvariable=self.region, state='readonly',
                                       values=sorted(phonenumbers.SUPPORTED_REGIONS), width=5)
        self.region_box.pack(side='left')
        self.platform_label = self.label(row, 'platform', bg=self.PANEL)
        self.platform_box = ttk.Combobox(row, textvariable=self.platform, state='readonly',
                                         values=list(PLATFORMS), width=11)
        self.platform_box.bind('<<ComboboxSelected>>', lambda _: self.select(self.mode))
        self.button = self.button_widget(row, 'run', self.start, primary=True)
        self.button.pack(side='right')
        results_header = tk.Frame(main, bg=self.BG)
        results_header.grid(row=3, column=0, sticky='ew', pady=(24, 12))
        self.label(results_header, 'results', color=self.FG, size=12).pack(side='left')
        tk.Label(results_header, textvariable=self.status, bg=self.BG, fg=self.ACCENT,
                 font=('Microsoft YaHei UI', 10)).pack(side='right')
        results = tk.Frame(main, bg=self.PANEL)
        results.grid(row=4, column=0, sticky='nsew')
        self.empty = tk.Frame(results, bg=self.PANEL)
        self.empty.pack(fill='both', expand=True)
        tk.Label(self.empty, text='◎', font=('Segoe UI', 36), bg=self.PANEL,
                 fg=self.ACCENT).pack(pady=(20, 0))
        self.empty_title = self.label(self.empty, 'empty', bg=self.PANEL, color=self.FG, size=15)
        self.empty_title.pack(pady=8)
        self.empty_help = self.label(self.empty, 'empty_help', bg=self.PANEL, wraplength=620)
        self.empty_help.pack(pady=(0, 15))
        self.tree = ttk.Treeview(results, columns=('key', 'value'), show='headings',
                                 style='Result.Treeview', selectmode='browse')
        self.tree.column('key', width=165, stretch=False)
        self.tree.column('value', width=470)
        self.scroll = ttk.Scrollbar(results, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scroll.set)
        self.tree.bind('<<TreeviewSelect>>', self.select_result)
        self.tree.bind('<Control-c>', self.copy_selected)
        self.tree.bind('<Control-C>', self.copy_selected)
        self.tree.bind('<Double-1>', self.copy_selected)
        self.detail = tk.Label(main, bg=self.BG, fg=self.MUTED, wraplength=740,
                               justify='left', anchor='w', font=('Microsoft YaHei UI', 9))
        self.detail.grid(row=5, column=0, sticky='ew', pady=(8, 0))
        actions = tk.Frame(main, bg=self.BG)
        actions.grid(row=6, column=0, sticky='ew', pady=(14, 10))
        self.button_widget(actions, 'copy_selected', self.copy_selected).pack(side='left', padx=(0, 8))
        self.button_widget(actions, 'copy', self.copy).pack(side='left')
        self.button_widget(actions, 'open_profile', self.open_profile).pack(side='left', padx=8)
        self.button_widget(actions, 'export', self.export).pack(side='right')
        self.notice = self.label(main, 'notice', wraplength=740)
        self.notice.grid(row=7, column=0, sticky='w')
        def resize(event):
            width = max(200, event.width - 44)
            for widget in (self.heading, self.hint, self.detail, self.notice, self.empty_help):
                widget.config(wraplength=width)
        main.bind('<Configure>', resize)
        self.refresh_language()
        root.after(100, self.poll)

    def label(self, parent, key, size=10, color=None, bg=None, **kwargs):
        widget = tk.Label(parent, bg=bg or self.BG, fg=color or self.MUTED,
                          font=('Microsoft YaHei UI', size), justify='left', **kwargs)
        self.bindings.append((widget, key))
        return widget

    def button_widget(self, parent, key, command, primary=False):
        button = tk.Button(parent, command=command, relief='flat', bd=0,
                            bg=self.ACCENT if primary else self.CARD,
                            fg=self.BG if primary else self.FG, activebackground='#7cebd0',
                            activeforeground=self.BG, cursor='hand2', padx=16, pady=10,
                            font=('Microsoft YaHei UI', 10, 'bold'))
        self.bindings.append((button, key))
        return button

    def change_language(self, _=None):
        self.lang = LANGUAGES[self.language.get()]
        self.refresh_language()

    def refresh_language(self):
        for widget, key in self.bindings:
            widget.config(text=UI[self.lang][key])
        self.tree.heading('key', text=UI[self.lang]['field'])
        self.tree.heading('value', text=UI[self.lang]['value'])
        self.status.set(UI[self.lang][self.state])
        self.select(self.mode)
        if self.result:
            self.show_result()
        elif self.state == 'failed':
            self.empty_title.config(text=UI[self.lang]['failed'])
            self.empty_help.config(text=UI[self.lang][self.error_key])
        elif self.busy:
            self.show_empty('busy', 'empty_help')

    def select(self, index):
        self.mode = index
        for n, button in enumerate(self.nav):
            button.config(bg='#21473f' if n == index else self.CARD,
                          fg=self.ACCENT if n == index else self.FG)
        self.hint.config(text=UI[self.lang]['hint_' + self.MODE_KEYS[index]])
        self.entry.config(state='disabled' if index == 1 else 'normal')
        self.region_box.config(state='readonly' if index == 2 else 'disabled')
        if index == 4:
            self.region_label.pack_forget()
            self.region_box.pack_forget()
            self.platform_label.pack(side='left', padx=(0, 8))
            self.platform_box.pack(side='left')
            hint = 'hint_uid' if self.platform.get() in ('Bilibili', 'Weibo') else 'hint_slug'
            self.hint.config(text=UI[self.lang][hint])
        else:
            self.platform_label.pack_forget()
            self.platform_box.pack_forget()
            self.region_label.pack(side='left', padx=(0, 8))
            self.region_box.pack(side='left')

    def set_state(self, key):
        self.state = key
        self.status.set(UI[self.lang][key])

    def start(self):
        if self.busy:
            return
        args = self.MODES[self.mode], self.value.get(), self.region.get(), self.lang, self.platform.get()
        self.busy = True
        self.button.config(state='disabled')
        self.set_state('busy')
        self.result = {}
        self.show_empty('busy', 'empty_help')
        def work():
            try:
                self.events.put((True, query(*args)))
            except (ValueError, phonenumbers.NumberParseException):
                self.events.put((False, 'input_error'))
            except Exception:
                self.events.put((False, 'network_error'))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            success, data = self.events.get_nowait()
            self.busy = False
            self.button.config(state='normal')
            if success:
                self.result = data
                self.show_result()
                self.set_state('done')
            else:
                self.error_key = data
                self.set_state('failed')
                self.show_empty('failed', data)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def show_empty(self, title, help_key):
        self.detail.config(text='')
        self.tree.pack_forget()
        self.scroll.pack_forget()
        self.empty.pack(fill='both', expand=True)
        self.empty_title.config(text=UI[self.lang][title])
        self.empty_help.config(text=UI[self.lang][help_key])

    def localized_result(self):
        return {localize(k, self.lang): localize(v, self.lang) for k, v in self.result.items()}

    def show_result(self):
        self.detail.config(text='')
        self.empty.pack_forget()
        self.scroll.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.delete(*self.tree.get_children())
        for key, value in self.localized_result().items():
            self.tree.insert('', 'end', values=(key, value))

    def select_result(self, _=None):
        selected = self.tree.selection()
        if selected:
            key, value = self.tree.item(selected[0], 'values')
            self.detail.config(text=f'{key}: {value}')

    def copy(self):
        if not self.result:
            self.status.set(UI[self.lang]['first'])
            return
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(f'{k}: {v}' for k, v in self.localized_result().items()))
        self.set_state('copied')

    def copy_selected(self, _=None):
        selected = self.tree.selection()
        if not selected or not self.result:
            self.status.set(UI[self.lang]['select_row'])
            return 'break'
        value = self.tree.item(selected[0], 'values')[1]
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.set_state('copied')
        return 'break'

    def open_profile(self):
        url = self.result.get('主页链接')
        if not url:
            self.status.set(UI[self.lang]['no_profile'])
            return
        webbrowser.open(url)

    def export(self):
        if not self.result:
            messagebox.showinfo(UI[self.lang]['info'], UI[self.lang]['first'])
            return
        path = filedialog.asksaveasfilename(defaultextension='.json',
                    filetypes=[('JSON', '*.json'), ('CSV', '*.csv')])
        if not path:
            return
        data = self.localized_result()
        try:
            if path.lower().endswith('.csv'):
                with open(path, 'w', encoding='utf-8-sig', newline='') as stream:
                    writer = csv.writer(stream)
                    writer.writerow([UI[self.lang]['field'], UI[self.lang]['value']])
                    for key, value in data.items():
                        value = str(value)
                        writer.writerow([key, "'" + value if value.startswith(('=', '+', '-', '@')) else value])
            else:
                with open(path, 'w', encoding='utf-8') as stream:
                    json.dump(data, stream, ensure_ascii=False, indent=2)
            self.set_state('saved')
        except OSError:
            messagebox.showerror(UI[self.lang]['export_failed'], UI[self.lang]['export_failed'])


if __name__ == '__main__':
    window = tk.Tk()
    App(window)
    window.mainloop()
