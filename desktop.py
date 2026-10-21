"""Windows desktop edition of HunxByts/GhostTrack."""
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import phonenumbers
from platforms import PLATFORMS, lookup_profile

from version import VERSION
from queries import query
from storage import Store
from archive import Archive, ArchiveError, flatten
from reports import write_report
from platforms import detect_platform, ProfileInputError, QueryCancelled
from datetime import datetime, timezone
from pathlib import Path
import logging
import sys
import time
from public_data import PublicQueryError, public_target




from i18n import LANGUAGES, UI, localize, platform_name


class App:
    BG, PANEL, CARD = '#080e17', '#101b2a', '#172638'
    FG, MUTED, ACCENT = '#e7f4f1', '#8da9b5', '#5cf0b7'
    MODES = ['IP 归属地', '本机公网 IP', '号码归属地', '用户名链接', '国内平台',
             '域名档案', 'DNS 记录', '网站与证书', 'IP 注册网络', 'GitHub 公开资料', '域名综合报告', '授权账号档案']
    MODE_KEYS = ['ip', 'self', 'phone', 'username', 'domestic', 'domain', 'dns', 'website', 'network', 'github', 'overview', 'archive']

    def __init__(self, root, data_dir=None):
        self.root, self.result = root, {}
        self.store = Store(data_dir)
        self.archive = Archive(self.store.directory)
        self.events = queue.Queue()
        self.lang, self.mode, self.busy = self.store.settings['language'], 10, False
        self.job_id, self.closed = 0, False
        self.cancel_event = threading.Event()
        self.network_slots = threading.BoundedSemaphore(2)
        self.context = None
        self.state = 'ready'
        self.value = tk.StringVar()
        region = self.store.settings['region']
        self.region = tk.StringVar(value=region if region in phonenumbers.SUPPORTED_REGIONS else 'CN')
        self.platform = tk.StringVar(value='Auto')
        self.platform_choice = tk.StringVar()
        self.language = tk.StringVar(value=next(k for k, v in LANGUAGES.items() if v == self.lang))
        self.filter = tk.StringVar()
        self.status = tk.StringVar()
        self.telemetry = tk.StringVar()
        self.elapsed = 0.0
        self.started = None
        self.bindings = []
        # Tk fonts use points while geometry uses pixels. Normalize both to the
        # available monitor so Windows DPI scaling cannot clip the navigation.
        self.scale = max(.75, min(root.winfo_fpixels('1i') / 96,
                                  (root.winfo_screenwidth() - 60) / 1180,
                                  (root.winfo_screenheight() - 100) / 840))
        root.tk.call('tk', 'scaling', self.scale * 96 / 72)
        root.title(f'GhostTrack / {VERSION}')
        root.geometry(f'{int(1180 * self.scale)}x{int(840 * self.scale)}')
        root.minsize(int(1040 * self.scale), int(700 * self.scale))
        root.configure(bg=self.BG)
        for option, value in (('background', self.CARD), ('foreground', self.FG),
                              ('selectBackground', '#203f52'), ('selectForeground', self.FG),
                              ('font', ('Microsoft YaHei UI', 10))):
            root.option_add('*TCombobox*Listbox.' + option, value)
        icon = Path(__file__).parent / 'assets' / 'ghosttrack.ico'
        if icon.exists():
            try:
                root.iconbitmap(str(icon))
            except tk.TclError:
                pass
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.bind('<Escape>', lambda _: self.cancel())
        root.bind('<Control-l>', lambda _: self.entry.focus_set())
        root.report_callback_exception = self.callback_error
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=self.CARD, background=self.CARD,
                        foreground=self.FG, arrowcolor=self.ACCENT, padding=7)
        style.map('TCombobox', fieldbackground=[('readonly', self.CARD)],
                  foreground=[('readonly', self.FG)], selectbackground=[('readonly', self.CARD)])
        style.configure('Result.Treeview', background=self.PANEL, fieldbackground=self.PANEL,
                        foreground=self.FG, rowheight=39, borderwidth=0, bordercolor=self.PANEL,
                        lightcolor=self.PANEL, darkcolor=self.PANEL, font=('Consolas', 10))
        style.configure('Result.Treeview.Heading', background=self.CARD, foreground=self.MUTED,
                        bordercolor=self.PANEL, lightcolor=self.PANEL, darkcolor=self.PANEL,
                        padding=12, font=('Microsoft YaHei UI', 10))
        style.configure('Result.Vertical.TScrollbar', background=self.CARD, troughcolor=self.PANEL,
                         arrowcolor=self.ACCENT, borderwidth=0)
        style.map('Result.Treeview', background=[('selected', '#203f52')])
        style.configure('Query.Horizontal.TProgressbar', background=self.ACCENT,
                         troughcolor=self.PANEL, borderwidth=0, thickness=4)
        px = lambda value: max(1, int(value * self.scale))
        side = tk.Frame(root, bg=self.PANEL, width=px(238))
        side.pack(side='left', fill='y')
        side.pack_propagate(False)
        self.brand = tk.Label(side, text='GHOSTTRACK', bg=self.PANEL, fg=self.ACCENT,
                              font=('Consolas', 18, 'bold'))
        self.brand.pack(anchor='w', padx=px(20), pady=(px(24), 4))
        tk.Label(side, text=f'PUBLIC DATA / DESK {VERSION}', bg=self.PANEL,
                 fg=self.MUTED, font=('Consolas', 8)).pack(anchor='w', padx=px(20), pady=(0, px(16)))
        self.label(side, 'tools', bg=self.PANEL, size=8).pack(anchor='w', padx=px(20), pady=(0, px(10)))
        self.nav = []
        for index, key in enumerate(self.MODE_KEYS):
            button = self.button_widget(side, key, lambda n=index: self.select(n))
            button.config(font=('Microsoft YaHei UI', 9), pady=px(4), anchor='w', padx=px(10),
                          wraplength=px(194), justify='left')
            button.pack(fill='x', padx=px(12), pady=px(2))
            self.nav.append(button)
        tk.Frame(side, height=1, bg='#263d50').pack(fill='x', padx=px(20), pady=px(12))
        utilities = tk.Frame(side, bg=self.PANEL)
        utilities.pack(fill='x', padx=px(12), pady=2)
        utilities.columnconfigure(0, weight=1)
        utilities.columnconfigure(1, weight=1)
        for index, (key, command) in enumerate((('history', self.history_dialog), ('archive_manage', self.archive_dialog),
                                                ('settings', self.settings_dialog), ('help', self.help_dialog))):
            utility = self.button_widget(utilities, key, command)
            utility.config(font=('Microsoft YaHei UI', 9), pady=px(7), padx=px(3),
                           wraplength=px(94))
            utility.grid(row=index // 2, column=index % 2, sticky='ew', padx=2, pady=2)
        footer = tk.Frame(side, bg=self.PANEL)
        footer.pack(side='bottom', fill='x', padx=px(20), pady=px(12))
        self.label(footer, 'privacy', bg=self.PANEL, wraplength=px(195), size=8).pack(anchor='w', pady=8)
        tk.Label(footer, text='Built on HunxByts/GhostTrack', bg=self.PANEL,
                 fg=self.MUTED, font=('Segoe UI', 8)).pack(anchor='w')
        main = tk.Frame(root, bg=self.BG)
        main.pack(side='left', fill='both', expand=True, padx=px(22), pady=px(20))
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        top = tk.Frame(main, bg=self.BG)
        top.grid(row=0, column=0, sticky='ew')
        self.label(top, 'workspace', size=9, color='#69d9cc').pack(side='left')
        language = ttk.Combobox(top, textvariable=self.language, values=list(LANGUAGES),
                                state='readonly', width=15)
        language.pack(side='right')
        tk.Label(top, text='PUBLIC SOURCES  /  LOCAL WORKSPACE', bg=self.BG, fg=self.MUTED,
                  font=('Consolas', 8)).pack(side='right', padx=px(16))
        language.bind('<<ComboboxSelected>>', self.change_language)
        hero = tk.Frame(main, bg=self.BG)
        hero.grid(row=1, column=0, sticky='ew', pady=(px(18), px(18)))
        headline = tk.Frame(hero, bg=self.BG)
        headline.pack(fill='x', pady=(0, px(16)))
        self.heading = self.label(headline, 'tagline', size=23, color=self.FG, wraplength=px(730))
        self.heading.pack(side='left', anchor='w')
        mark = tk.Canvas(headline, width=px(88), height=px(44), bg=self.BG, highlightthickness=0)
        mark.pack(side='right')
        for x in range(8, 89, 14):
            mark.create_line(px(x), px(8), px(x), px(36), fill='#1c3043')
        mark.create_line(px(8), px(22), px(78), px(22), fill='#29465b')
        mark.create_oval(px(30), px(7), px(60), px(37), outline='#69d9cc', width=2)
        mark.create_line(px(45), px(22), px(66), px(7), fill=self.ACCENT, width=2)
        mark.create_oval(px(42), px(19), px(48), px(25), fill=self.ACCENT, outline='')
        metrics = tk.Frame(hero, bg=self.BG)
        metrics.pack(fill='x')
        self.metric_values = [tk.StringVar() for _ in range(3)]
        for n, key in enumerate(('modules_metric', 'fields_metric', 'elapsed_metric')):
            metrics.columnconfigure(n, weight=1)
            card = tk.Frame(metrics, bg=self.PANEL, highlightbackground='#263d50', highlightthickness=1)
            card.grid(row=0, column=n, sticky='ew', padx=(0, px(10) if n < 2 else 0))
            strip = tk.Frame(card, bg=('#69d9cc', self.ACCENT, '#b5a6ff')[n], width=3)
            strip.pack(side='left', fill='y')
            tk.Label(card, textvariable=self.metric_values[n], bg=self.PANEL,
                     fg=('#69d9cc', self.ACCENT, '#c0b4ff')[n],
                     font=('Consolas', 24, 'bold')).pack(side='left', padx=px(14), pady=px(11))
            self.label(card, key, bg=self.PANEL, size=9).pack(side='left', padx=(0, px(8)))
        body = tk.Frame(main, bg=self.BG)
        body.grid(row=2, column=0, sticky='nsew')
        body.columnconfigure(0, weight=0, minsize=px(266))
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        form = tk.Frame(body, bg=self.PANEL, width=px(266), padx=px(16), pady=px(14),
                        highlightbackground='#263d50', highlightthickness=1)
        form.grid(row=0, column=0, sticky='nsew', padx=(0, px(14)))
        form.pack_propagate(False)
        execution = tk.Frame(form, bg=self.PANEL)
        execution.pack(side='bottom', fill='x')
        form_top = tk.Frame(form, bg=self.PANEL)
        form_top.pack(fill='x')
        tk.Label(form_top, text='01 /', bg=self.PANEL, fg='#69d9cc', font=('Consolas', 11, 'bold')).pack(side='left', padx=(0, 8))
        self.label(form_top, 'parameters', bg=self.PANEL, color=self.FG, size=10,
                   wraplength=px(190)).pack(side='left')
        self.source_badge = tk.Label(form, bg='#142c36', fg='#69d9cc', font=('Consolas', 8),
                                     padx=px(9), pady=px(5), anchor='w', justify='left', wraplength=px(210))
        self.source_badge.pack(fill='x', pady=(px(7), px(8)))
        self.label(form, 'input', bg=self.PANEL, size=8, wraplength=px(231)).pack(anchor='w', pady=(0, px(6)))
        self.entry = tk.Entry(form, textvariable=self.value, bg=self.CARD, fg=self.FG,
                              disabledbackground=self.CARD, disabledforeground=self.MUTED,
                              insertbackground=self.ACCENT, relief='flat', highlightthickness=1,
                              highlightbackground='#2b435a', highlightcolor=self.ACCENT,
                              font=('Segoe UI', 13), width=1)
        self.entry.pack(fill='x', ipady=px(9))
        self.entry.bind('<Return>', lambda _: self.start())
        input_actions = tk.Frame(form, bg=self.PANEL)
        input_actions.pack(fill='x', pady=(px(6), px(8)))
        input_actions.columnconfigure(0, weight=1)
        input_actions.columnconfigure(1, weight=1)
        paste_button = self.button_widget(input_actions, 'paste', self.paste)
        paste_button.config(font=('Microsoft YaHei UI', 9), padx=px(4), pady=px(7))
        paste_button.grid(row=0, column=0, sticky='ew', padx=(0, px(4)))
        self.example_button = self.button_widget(input_actions, 'example', self.use_example)
        self.example_button.config(font=('Microsoft YaHei UI', 9), padx=px(4), pady=px(7))
        self.example_button.grid(row=0, column=1, sticky='ew', padx=(px(4), 0))
        self.hint = tk.Label(form, bg=self.PANEL, fg=self.MUTED,
                             font=('Microsoft YaHei UI', 9), anchor='nw', justify='left', wraplength=px(225))
        self.hint.pack(fill='x', pady=(0, px(6)))
        row = tk.Frame(form, bg=self.PANEL)
        row.pack(fill='x', pady=(0, px(8)))
        self.region_label = self.label(row, 'region', bg=self.PANEL)
        self.region_label.pack(side='left', padx=(0, 8))
        self.region_box = ttk.Combobox(row, textvariable=self.region, state='readonly',
                                       values=sorted(phonenumbers.SUPPORTED_REGIONS), width=5)
        self.region_box.pack(side='left')
        self.platform_label = self.label(row, 'platform', bg=self.PANEL)
        self.platform_box = ttk.Combobox(row, textvariable=self.platform_choice, state='readonly', width=15)
        self.platform_box.bind('<<ComboboxSelected>>', self.choose_platform)
        tk.Frame(execution, bg='#263d50', height=1).pack(fill='x', pady=(px(6), px(10)))
        run_row = tk.Frame(execution, bg=self.PANEL)
        run_row.pack(fill='x')
        run_row.columnconfigure(0, weight=1)
        self.button = self.button_widget(run_row, 'run', self.start, primary=True)
        self.button.config(pady=px(9), padx=px(5), font=('Microsoft YaHei UI', 9, 'bold'))
        self.button.grid(row=0, column=0, sticky='ew')
        self.cancel_button = self.button_widget(run_row, 'cancel', self.cancel)
        self.cancel_button.config(font=('Microsoft YaHei UI', 9), pady=px(9), padx=px(8))
        self.cancel_button.grid(row=0, column=1, sticky='ew', padx=(px(6), 0))
        self.cancel_button.config(state='disabled')
        result_panel = tk.Frame(body, bg=self.PANEL, padx=px(16), pady=px(16),
                                highlightbackground='#263d50', highlightthickness=1)
        result_panel.grid(row=0, column=1, sticky='nsew')
        result_panel.columnconfigure(0, weight=1)
        result_panel.rowconfigure(2, weight=1)
        results_header = tk.Frame(result_panel, bg=self.PANEL)
        results_header.grid(row=0, column=0, sticky='ew', pady=(0, px(12)))
        tk.Label(results_header, text='02 /', bg=self.PANEL, fg='#69d9cc', font=('Consolas', 11, 'bold')).pack(side='left', padx=(0, 8))
        self.label(results_header, 'results', bg=self.PANEL, color=self.FG, size=12).pack(side='left')
        self.progress = ttk.Progressbar(results_header, mode='indeterminate', length=70,
                                        style='Query.Horizontal.TProgressbar')
        tk.Label(results_header, text='JSON / CSV / HTML', bg=self.PANEL, fg=self.MUTED,
                 font=('Consolas', 8)).pack(side='right')
        filter_row = tk.Frame(result_panel, bg=self.PANEL)
        filter_row.grid(row=1, column=0, sticky='ew', pady=(0, px(12)))
        self.label(filter_row, 'filter', bg=self.PANEL, size=8, wraplength=px(155)).pack(side='left', padx=(0, px(10)))
        self.filter_entry = tk.Entry(filter_row, textvariable=self.filter, bg=self.CARD, fg=self.FG,
                                      insertbackground=self.ACCENT, relief='flat', width=12,
                                      highlightthickness=1, highlightbackground='#2b435a', highlightcolor=self.ACCENT,
                                      font=('Microsoft YaHei UI', 10))
        self.filter_entry.pack(side='left', fill='x', expand=True, ipady=px(7))
        self.filter.trace_add('write', lambda *_: self.show_result() if self.result else None)
        self.filter_entry.bind('<Escape>', lambda _: self.filter.set(''))
        results = tk.Frame(result_panel, bg=self.BG, highlightbackground='#263d50', highlightthickness=1)
        results.grid(row=2, column=0, sticky='nsew')
        self.empty = tk.Frame(results, bg=self.BG)
        self.empty.pack(fill='both', expand=True)
        radar = tk.Canvas(self.empty, width=px(300), height=px(134), bg=self.BG, highlightthickness=0)
        radar.pack(pady=(px(16), 0))
        for x in range(20, 300, 20):
            radar.create_line(px(x), px(14), px(x), px(110), fill='#142536')
        for y in range(14, 120, 16):
            radar.create_line(px(20), px(y), px(280), px(y), fill='#142536')
        for radius in (18, 34, 48):
            radar.create_oval(px(150-radius), px(61-radius), px(150+radius), px(61+radius), outline='#2a5262')
        radar.create_arc(px(102), px(13), px(198), px(109), start=15, extent=110, style='arc', outline='#69d9cc', width=2)
        radar.create_line(px(150), px(61), px(182), px(29), fill=self.ACCENT, width=2)
        radar.create_oval(px(147), px(58), px(153), px(64), fill=self.ACCENT, outline='')
        for x, direction in ((22, 1), (278, -1)):
            for y, vertical in ((14, 1), (110, -1)):
                radar.create_line(px(x), px(y + vertical*10), px(x), px(y), px(x + direction*16), px(y), fill='#69d9cc')
        self.empty_title = self.label(self.empty, 'empty', bg=self.BG, color=self.FG, size=14, wraplength=px(440))
        self.empty_title.pack(pady=8)
        self.empty_help = self.label(self.empty, 'empty_help', bg=self.BG, wraplength=px(420), size=9)
        self.empty_help.pack(pady=(0, 15))
        self.tree = ttk.Treeview(results, columns=('key', 'value'), show='headings',
                                 style='Result.Treeview', selectmode='browse')
        self.tree.column('key', width=px(178), minwidth=px(110), stretch=False)
        self.tree.column('value', width=px(330), minwidth=px(140))
        self.tree.tag_configure('even', background=self.PANEL)
        self.tree.tag_configure('odd', background='#122133')
        self.scroll = ttk.Scrollbar(results, command=self.tree.yview, style='Result.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=self.scroll.set)
        self.tree.bind('<<TreeviewSelect>>', self.select_result)
        self.tree.bind('<Control-c>', self.copy_selected)
        self.tree.bind('<Control-C>', self.copy_selected)
        self.tree.bind('<Double-1>', self.copy_selected)
        self.detail = tk.Text(result_panel, bg='#142231', fg=self.FG, height=3, width=1, state='disabled',
                              wrap='word', relief='flat', highlightthickness=1, highlightbackground='#263d50',
                              padx=px(12), pady=px(10), font=('Microsoft YaHei UI', 9))
        self.detail.grid(row=3, column=0, sticky='ew', pady=(px(10), 0))
        self.detail.grid_remove()
        self.status_label = tk.Label(main, textvariable=self.status, bg=self.BG, fg=self.ACCENT,
                                     font=('Microsoft YaHei UI', 10), anchor='w', justify='left')
        self.status_label.grid(row=3, column=0, sticky='ew', pady=(px(12), 0))
        actions = tk.Frame(result_panel, bg=self.PANEL)
        actions.grid(row=4, column=0, sticky='ew', pady=(px(12), 0))
        self.action_buttons = []
        for key, command in (('copy_selected', self.copy_selected), ('copy', self.copy),
                             ('open_profile', self.open_profile), ('export', self.export),
                             ('save_archive', self.save_archive)):
            widget = self.button_widget(actions, key, command)
            widget.config(font=('Microsoft YaHei UI', 9, 'bold'), padx=px(6), pady=px(8), wraplength=px(140))
            self.action_buttons.append(widget)
        action_columns = [0]
        def arrange_actions(event):
            columns = 3 if event.width >= px(510) else 2
            if action_columns[0] == columns:
                return
            action_columns[0] = columns
            for column in range(3):
                actions.columnconfigure(column, weight=1 if column < columns else 0, uniform='actions' if column < columns else '')
            for index, widget in enumerate(self.action_buttons):
                widget.grid(row=index // columns, column=index % columns, sticky='ew',
                            padx=(0, px(6) if index % columns < columns - 1 else 0), pady=(0, px(6)))
        actions.bind('<Configure>', arrange_actions)
        self.notice = self.label(main, 'notice', wraplength=px(740), size=8)
        self.notice.grid(row=4, column=0, sticky='w', pady=(px(4), 0))
        def resize(event):
            width = max(px(200), event.width - px(44))
            for widget in (self.heading, self.notice, self.status_label):
                widget.config(wraplength=width)
        main.bind('<Configure>', resize)
        def resize_results(event):
            width = max(px(180), event.width - px(30))
            for widget in (self.empty_title, self.empty_help):
                widget.config(wraplength=width)
        results.bind('<Configure>', resize_results)
        self.refresh_language()
        self.update_actions()
        if self.store.warning:
            self.status.set(UI[self.lang]['state_warning'])
        root.after(100, self.poll)

    def label(self, parent, key, size=10, color=None, bg=None, **kwargs):
        widget = tk.Label(parent, bg=bg or self.BG, fg=color or self.MUTED,
                          font=('Microsoft YaHei UI', size), justify='left', **kwargs)
        self.bindings.append((widget, key))
        return widget

    def button_widget(self, parent, key, command, primary=False):
        button = tk.Button(parent, command=command, relief='flat', bd=0, highlightthickness=1, highlightbackground='#2b435a', highlightcolor=self.ACCENT,
                            bg=self.ACCENT if primary else self.CARD,
                            fg=self.BG if primary else self.FG, activebackground='#7cf6ca',
                            activeforeground=self.BG, cursor='hand2', padx=16, pady=10,
                            font=('Microsoft YaHei UI', 10, 'bold'))
        button.bind('<Enter>', lambda _: button.config(highlightbackground=self.ACCENT) if str(button['state']) != 'disabled' else None)
        button.bind('<Leave>', lambda _: button.config(highlightbackground='#2b435a'))
        self.bindings.append((button, key))
        return button

    def change_language(self, _=None):
        self.lang = LANGUAGES[self.language.get()]
        self.refresh_language()
        self.store.settings['language'] = self.lang
        if not self.store.save():
            self.status.set(UI[self.lang]['state_warning'])

    def refresh_language(self):
        for widget, key in self.bindings:
            widget.config(text=UI[self.lang][key])
        self.tree.heading('key', text=UI[self.lang]['field'], anchor='w')
        self.tree.heading('value', text=UI[self.lang]['value'], anchor='w')
        self.status.set(UI[self.lang][self.state])
        self.update_telemetry()
        self.filter_entry.config(takefocus=True)
        self.select(self.mode)
        if self.result:
            self.show_result()
        elif self.state == 'failed':
            self.empty_title.config(text=UI[self.lang]['failed'])
            self.empty_help.config(text=UI[self.lang][self.error_key])
        elif self.busy:
            self.show_empty('busy', 'empty_help')

    def use_example(self):
        if self.busy:
            return
        examples = ['8.8.8.8', '', '+12025550123', 'octocat',
                    'https://space.bilibili.com/2', 'example.com', 'example.com',
                    'https://www.python.org/', 'AS15169', 'octocat', 'python.org', '+8613800138000']
        self.value.set(examples[self.mode])
        if self.mode == 4:
            self.platform.set('Bilibili')
            self.select(4)
        self.entry.focus_set()

    def select(self, index):
        changed = index != self.mode
        if self.busy and index != self.mode:
            self.cancel()
        self.mode = index
        if changed:
            self.result = {}
            self.context = None
            self.elapsed = 0.0
            self.value.set('')
            self.filter.set('')
            self.set_state('ready')
            self.show_empty('empty', 'empty_help')
            self.update_actions()
            self.update_telemetry()
        sources = ['IPWHO.IS', 'IPIFY + IPWHO.IS', 'LOCAL METADATA', 'PUBLIC LINKS',
                   'PUBLIC PROFILE HTML', 'RDAP', 'DNS OVER HTTPS', 'HTTPS / TLS',
                   'RDAP / IP / ASN', 'GITHUB REST', 'RDAP + DNS + HTTPS', 'LOCAL AUTHORIZED ARCHIVE']
        self.source_badge.config(text=sources[index])
        self.example_button.config(state='disabled' if self.busy or index == 1 else 'normal')
        self.platform_choice.set(platform_name(self.platform.get(), self.lang))
        self.platform_box.config(values=[platform_name(p, self.lang) for p in ('Auto', *PLATFORMS)])
        for n, button in enumerate(self.nav):
            button.config(text=f'{n+1:02d} / {UI[self.lang][self.MODE_KEYS[n]]}',
                          bg='#1b3944' if n == index else self.CARD,
                          fg=self.ACCENT if n == index else self.FG)
        self.heading.config(text=f'{index+1:02d} / {UI[self.lang][self.MODE_KEYS[index]]}')
        self.hint.config(text=UI[self.lang]['hint_' + self.MODE_KEYS[index]])
        self.entry.config(state='disabled' if index == 1 or self.busy else 'normal')
        self.region_box.config(state='readonly' if index == 2 else 'disabled')
        if index == 4:
            self.region_label.pack_forget()
            self.region_box.pack_forget()
            self.platform_label.pack(side='left', padx=(0, 8))
            self.platform_box.pack(side='left')
            hint = 'hint_share' if self.platform.get() in ('Auto', 'Douyin', 'Xiaohongshu', 'Kuaishou') else (
                'hint_uid' if self.platform.get() in ('Bilibili', 'Weibo') else 'hint_slug')
            self.hint.config(text=UI[self.lang][hint])
            self.platform_box.config(state='disabled' if self.busy else 'readonly')
        else:
            self.platform_label.pack_forget()
            self.platform_box.pack_forget()
            if index == 2:
                self.region_label.pack(side='left', padx=(0, 8))
                self.region_box.pack(side='left')
            else:
                self.region_label.pack_forget()
                self.region_box.pack_forget()

    def choose_platform(self, _=None):
        for name in ('Auto', *PLATFORMS):
            if platform_name(name, self.lang) == self.platform_choice.get():
                self.platform.set(name)
                break
        self.select(self.mode)

    def paste(self):
        if self.busy:
            return
        try:
            self.value.set(self.root.clipboard_get()[:5000])
            if self.mode == 4:
                detected = detect_platform(self.value.get())
                if detected:
                    self.platform.set(detected)
                    self.select(4)
        except tk.TclError:
            self.status.set(UI[self.lang]['clipboard_empty'])
        except ValueError:
            pass

    def set_state(self, key):
        self.state = key
        self.status.set(UI[self.lang][key])
        self.status_label.config(fg='#f1c781' if key in ('limited', 'failed') else self.ACCENT)

    def update_telemetry(self):
        self.telemetry.set(f'{len(self.MODES):02d} MODULES / {len(self.result):02d} FIELDS / {self.elapsed:.2f}s')
        for variable, value in zip(self.metric_values, (f'{len(self.MODES):02d}', f'{len(self.result):02d}', f'{self.elapsed:.1f}s')):
            variable.set(value)

    def start(self):
        if self.busy:
            return
        if not self.network_slots.acquire(blocking=False):
            self.status.set(UI[self.lang]['thread_wait'])
            return
        args = self.MODES[self.mode], self.value.get().strip(), self.region.get(), self.lang, self.platform.get()
        self.context = args
        self.job_id += 1
        job_id = self.job_id
        self.cancel_event = threading.Event()
        cancel = self.cancel_event
        self.busy = True
        self.started = time.monotonic()
        self.elapsed = 0.0
        self.button.config(state='disabled')
        self.example_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.entry.config(state='disabled')
        self.platform_box.config(state='disabled')
        self.set_state('busy')
        self.progress.pack(side='left', padx=12)
        self.progress.start(15)
        self.result = {}
        self.update_telemetry()
        self.filter.set('')
        self.update_actions()
        self.show_empty('busy', 'empty_help')
        def work():
            try:
                data = query(*args, cancel=cancel, archive=self.archive,
                             progress=lambda data: self.events.put((job_id, 'progress', data, args)))
                data.setdefault('查询时间 UTC', datetime.now(timezone.utc).isoformat(timespec='seconds'))
                data['查询工具'] = args[0]
                data['查询输入'] = args[1] if args[0] != '本机公网 IP' else '—'
                if not cancel.is_set():
                    self.events.put((job_id, True, data, args))
            except QueryCancelled:
                pass
            except ProfileInputError as error:
                self.events.put((job_id, False, error.code, args))
            except PublicQueryError as error:
                self.events.put((job_id, False, error.code, args))
            except (ValueError, phonenumbers.NumberParseException):
                self.events.put((job_id, False, 'input_error', args))
            except Exception as error:
                logging.warning('Query failed (%s)', type(error).__name__)
                self.events.put((job_id, False, 'network_error', args))
            finally:
                self.network_slots.release()
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        if self.closed:
            return
        if self.busy and self.started is not None:
            self.elapsed = time.monotonic() - self.started
            self.update_telemetry()
        try:
            job_id, success, data, args = self.events.get_nowait()
            if job_id != self.job_id:
                self.root.after(100, self.poll)
                return
            if success == 'progress':
                self.status.set(UI[self.lang]['source_progress'].format(**data))
                self.root.after(100, self.poll)
                return
            self.busy = False
            self.elapsed = time.monotonic() - self.started if self.started is not None else 0.0
            self.progress.stop()
            self.progress.pack_forget()
            self.button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.select(self.mode)
            if success:
                self.result = data
                self.show_result()
                limited = ((data.get('页面状态') and '已读取页面元信息' not in data['页面状态'])
                           or data.get('查询状态') == '部分来源不可用')
                self.set_state('limited' if limited else 'done')
                if args and not self.store.record(args[0], args[1], args[2], args[4], data):
                    self.status.set(UI[self.lang]['state_warning'])
            else:
                self.error_key = data
                self.set_state('failed')
                self.show_empty('failed', data)
            self.update_actions()
            self.update_telemetry()
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def cancel(self):
        if not self.busy:
            return
        self.cancel_event.set()
        self.job_id += 1
        self.busy = False
        self.elapsed = time.monotonic() - self.started if self.started is not None else 0.0
        self.update_telemetry()
        self.progress.stop()
        self.progress.pack_forget()
        self.button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.select(self.mode)
        self.set_state('cancelled')
        self.show_empty('cancelled', 'empty_help')

    def update_actions(self):
        for button in self.action_buttons:
            button.config(state='normal' if self.result else 'disabled')
        self.action_buttons[2].config(state='normal' if self.result.get('主页链接') or self.result.get('来源链接') else 'disabled')
        archivable = self.result.get('平台') in PLATFORMS and bool(self.result.get('主页链接'))
        self.action_buttons[4].config(state='normal' if archivable else 'disabled')

    def show_empty(self, title, help_key):
        self.set_detail('')
        self.detail.grid_remove()
        self.tree.pack_forget()
        self.scroll.pack_forget()
        self.empty.pack(fill='both', expand=True)
        self.empty_title.config(text=UI[self.lang][title])
        self.empty_help.config(text=UI[self.lang][help_key])

    def localized_result(self):
        def key_label(key):
            if ' / ' in key:
                prefix, suffix = key.split(' / ', 1)
                return prefix + ' / ' + str(localize(suffix, self.lang))
            return localize(key, self.lang)
        return {key_label(k): (UI[self.lang].get(v, v) if k.endswith('失败原因') else localize(v, self.lang))
                for k, v in self.result.items()}

    def show_result(self):
        self.set_detail(UI[self.lang]['select_row'])
        self.detail.grid()
        self.empty.pack_forget()
        self.scroll.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.delete(*self.tree.get_children())
        self.visible_rows = {}
        needle = self.filter.get().casefold().strip()
        for key, value in self.localized_result().items():
            if not needle or needle in f'{key} {value}'.casefold():
                preview = ' / '.join(str(value).splitlines())
                row = self.tree.insert('', 'end', values=(key, preview[:600]), tags=('even' if len(self.tree.get_children()) % 2 == 0 else 'odd',))
                self.visible_rows[row] = (key, str(value))

    def select_result(self, _=None):
        selected = self.tree.selection()
        if selected:
            key, value = self.visible_rows[selected[0]]
            self.set_detail(f'{key}: {value}')

    def set_detail(self, text):
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('1.0', text)
        self.detail.config(state='disabled')

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
        value = self.visible_rows[selected[0]][1]
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.set_state('copied')
        return 'break'

    def open_profile(self):
        url = self.result.get('主页链接') or self.result.get('来源链接')
        if not url:
            self.status.set(UI[self.lang]['no_profile'])
            return
        try:
            if url.startswith('http://') and any(host in url for host in ('v.douyin.com/', 'xhslink.com/')):
                url = 'https://' + url.split('://', 1)[1]
            public_target(url)
            webbrowser.open(url)
        except (ValueError, TypeError):
            self.status.set(UI[self.lang]['unsupported_platform'])

    def dialog(self, key, geometry='720x500'):
        window = tk.Toplevel(self.root)
        window.title(UI[self.lang][key] + ' · GhostTrack')
        window.configure(bg=self.BG)
        window.geometry(geometry)
        window.transient(self.root)
        window.grab_set()
        return window

    def history_dialog(self):
        window = self.dialog('history', '820x540')
        title = tk.Label(window, text=UI[self.lang]['history_title'], bg=self.BG, fg=self.FG,
                          font=('Microsoft YaHei UI', 16))
        title.pack(anchor='w', padx=24, pady=20)
        listing = tk.Listbox(window, bg=self.PANEL, fg=self.FG, relief='flat',
                             selectbackground='#203f52', font=('Microsoft YaHei UI', 10),
                             activestyle='none', exportselection=False)
        listing.pack(fill='both', expand=True, padx=24)
        def populate():
            listing.delete(0, 'end')
            for item in self.store.history:
                title = item['result'].get('平台', localize(item['kind'], self.lang))
                listing.insert('end', f"{item['time'][:19]}  ·  {title}  ·  {item['input'][:75]}")
            if not self.store.history:
                listing.insert('end', UI[self.lang]['no_history'])
        populate()
        def restore(_=None):
            selected = listing.curselection()
            if not selected or not self.store.history:
                return
            item = self.store.history[selected[0]]
            if item['kind'] not in self.MODES:
                return
            self.cancel()
            self.value.set(item['input'])
            self.region.set(item['region'])
            self.platform.set(item['platform'] if item['platform'] in PLATFORMS else 'Auto')
            self.select(self.MODES.index(item['kind']))
            self.result = dict(item['result'])
            self.filter.set('')
            self.show_result()
            limited = ((self.result.get('页面状态') and '已读取页面元信息' not in self.result['页面状态'])
                       or self.result.get('查询状态') == '部分来源不可用')
            self.set_state('limited' if limited else 'done')
            self.elapsed = 0.0
            self.update_telemetry()
            self.update_actions()
            window.destroy()
        def clear():
            if not self.store.history:
                return
            if messagebox.askyesno(UI[self.lang]['history'], UI[self.lang]['clear_confirm'], parent=window):
                if not self.store.clear_history():
                    self.status.set(UI[self.lang]['state_warning'])
                populate()
        listing.bind('<Double-1>', restore)
        listing.bind('<Return>', restore)
        row = tk.Frame(window, bg=self.BG)
        row.pack(fill='x', padx=24, pady=20)
        tk.Button(row, text=UI[self.lang]['restore'], command=restore, bg=self.ACCENT,
                  fg=self.BG, relief='flat', padx=20, pady=10).pack(side='left')
        tk.Button(row, text=UI[self.lang]['clear_history'], command=clear, bg=self.CARD,
                  fg=self.FG, relief='flat', padx=20, pady=10).pack(side='right')

    def settings_dialog(self):
        window = self.dialog('settings', '720x410')
        remember = tk.BooleanVar(value=self.store.settings['remember'])
        region = tk.StringVar(value=self.region.get())
        tk.Label(window, text=UI[self.lang]['settings'], bg=self.BG, fg=self.FG,
                 font=('Microsoft YaHei UI', 18)).pack(anchor='w', padx=24, pady=24)
        tk.Checkbutton(window, text=UI[self.lang]['remember'], variable=remember,
                        bg=self.BG, fg=self.FG, selectcolor=self.CARD, activebackground=self.BG,
                        activeforeground=self.FG, font=('Microsoft YaHei UI', 11)).pack(anchor='w', padx=24)
        tk.Label(window, text=UI[self.lang]['remember_help'], bg=self.BG, fg=self.MUTED,
                 wraplength=650, justify='left', font=('Microsoft YaHei UI', 10)).pack(anchor='w', padx=24, pady=16)
        row = tk.Frame(window, bg=self.BG)
        row.pack(fill='x', padx=24, pady=12)
        tk.Label(row, text=UI[self.lang]['region'], bg=self.BG, fg=self.FG).pack(side='left', padx=(0, 12))
        ttk.Combobox(row, textvariable=region, values=sorted(phonenumbers.SUPPORTED_REGIONS),
                     state='readonly', width=6).pack(side='left')
        def save():
            self.region.set(region.get())
            self.store.settings.update(remember=remember.get(), region=region.get(), language=self.lang)
            self.status.set(UI[self.lang]['saved_settings' if self.store.save() else 'state_warning'])
            window.destroy()
        tk.Button(window, text=UI[self.lang]['save'], command=save, bg=self.ACCENT,
                  fg=self.BG, padx=24, pady=12, relief='flat').pack(side='bottom', anchor='e', padx=24, pady=20)

    def help_dialog(self):
        window = self.dialog('help', '830x650')
        tk.Label(window, text=f'GhostTrack Desktop {VERSION}', bg=self.BG, fg=self.ACCENT,
                 font=('Segoe UI', 20, 'bold')).pack(anchor='w', padx=24, pady=20)
        text = tk.Text(window, bg=self.PANEL, fg=self.FG, relief='flat', wrap='word',
                        padx=20, pady=20, font=('Microsoft YaHei UI', 11))
        text.pack(fill='both', expand=True, padx=24)
        text.insert('1.0', UI[self.lang]['help_body'])
        text.config(state='disabled')
        tk.Button(window, text=UI[self.lang]['releases'], bg=self.CARD, fg=self.FG, relief='flat',
                  padx=20, pady=12, command=lambda: webbrowser.open(
                      'https://github.com/Serennity007/GhostTrack/releases')).pack(anchor='e', padx=24, pady=20)

    def save_archive(self):
        platform = self.result.get('平台')
        url = self.result.get('主页链接')
        if platform not in PLATFORMS or not url:
            self.status.set(UI[self.lang]['no_profile'])
            return
        window = self.dialog('save_archive', '640x560')
        tk.Label(window, text=UI[self.lang]['save_archive'], bg=self.BG, fg=self.FG,
                 font=('Microsoft YaHei UI', 16)).pack(anchor='w', padx=24, pady=(20, 4))
        tk.Label(window, text=UI[self.lang]['archive_consent'], bg=self.BG, fg=self.MUTED,
                 wraplength=590, justify='left', font=('Microsoft YaHei UI', 9)).pack(anchor='w', padx=24, pady=(0, 12))
        tk.Label(window, text=f"{localize('平台', self.lang)}: {platform_name(platform, self.lang)}",
                 bg=self.BG, fg=self.FG, font=('Microsoft YaHei UI', 10)).pack(anchor='w', padx=24, pady=2)
        tk.Label(window, text=url, bg=self.BG, fg=self.MUTED, wraplength=590, justify='left',
                 font=('Consolas', 9)).pack(anchor='w', padx=24, pady=(0, 12))
        phone = tk.StringVar()
        note = tk.StringVar()
        source = tk.StringVar(value=UI[self.lang]['source_self'])
        for key, variable in (('phone_number', phone), ('note', note)):
            tk.Label(window, text=UI[self.lang][key], bg=self.BG, fg=self.FG,
                     font=('Microsoft YaHei UI', 10)).pack(anchor='w', padx=24, pady=(8, 2))
            tk.Entry(window, textvariable=variable, bg=self.CARD, fg=self.FG, relief='flat',
                     insertbackground=self.ACCENT, font=('Microsoft YaHei UI', 11)).pack(fill='x', padx=24, ipady=6)
        tk.Label(window, text=UI[self.lang]['source'], bg=self.BG, fg=self.FG,
                 font=('Microsoft YaHei UI', 10)).pack(anchor='w', padx=24, pady=(8, 2))
        ttk.Combobox(window, textvariable=source, state='readonly',
                     values=[UI[self.lang]['source_self'], UI[self.lang]['source_public']]).pack(fill='x', padx=24)
        def submit():
            kind = 'self' if source.get() == UI[self.lang]['source_self'] else 'public'
            try:
                _, created, saved = self.archive.add(phone.get(), platform, url,
                                                     self.region.get(), kind, note.get())
            except ArchiveError as error:
                self.status.set(UI[self.lang][error.code])
                return
            if not saved:
                self.status.set(UI[self.lang]['state_warning'])
            else:
                self.set_state('archive_added' if created else 'archive_updated')
            window.destroy()
        tk.Button(window, text=UI[self.lang]['save'], command=submit, bg=self.ACCENT,
                  fg=self.BG, padx=24, pady=12, relief='flat').pack(side='bottom', anchor='e', padx=24, pady=20)

    def archive_dialog(self):
        window = self.dialog('archive_manage', '860x560')
        tk.Label(window, text=UI[self.lang]['archive_title'], bg=self.BG, fg=self.FG,
                 font=('Microsoft YaHei UI', 16)).pack(anchor='w', padx=24, pady=(20, 4))
        tk.Label(window, text=UI[self.lang]['archive_consent'], bg=self.BG, fg=self.MUTED,
                 wraplength=800, justify='left', font=('Microsoft YaHei UI', 9)).pack(anchor='w', padx=24, pady=(0, 10))
        listing = tk.Listbox(window, bg=self.PANEL, fg=self.FG, relief='flat',
                             selectbackground='#203f52', font=('Microsoft YaHei UI', 10),
                             activestyle='none', exportselection=False)
        listing.pack(fill='both', expand=True, padx=24)
        def populate():
            listing.delete(0, 'end')
            for item in self.archive.records:
                listing.insert('end', f"{item['added'][:19]}  ·  {platform_name(item['platform'], self.lang)}  ·  "
                                      f"{item['phone_display']}  ·  {item['url'][:60]}")
            if not self.archive.records:
                listing.insert('end', UI[self.lang]['archive_empty'])
        populate()
        def selected_record():
            selected = listing.curselection()
            if not selected or not self.archive.records or selected[0] >= len(self.archive.records):
                return None
            return self.archive.records[selected[0]]
        def delete():
            item = selected_record()
            if not item:
                return
            if messagebox.askyesno(UI[self.lang]['archive_manage'],
                                   UI[self.lang]['archive_delete_confirm'], parent=window):
                if not self.archive.remove(item['id']):
                    self.status.set(UI[self.lang]['state_warning'])
                else:
                    self.set_state('archive_deleted')
                populate()
        def export_all():
            if not self.archive.records:
                self.status.set(UI[self.lang]['archive_empty'])
                return
            path = filedialog.asksaveasfilename(defaultextension='.json',
                        initialfile=f'GhostTrack-archive-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json',
                        filetypes=[('JSON', '*.json'), ('CSV', '*.csv'), ('HTML report', '*.html')], parent=window)
            if not path:
                return
            try:
                write_report(path, flatten(self.archive.records), (UI[self.lang]['field'], UI[self.lang]['value']))
                self.set_state('saved')
            except OSError:
                messagebox.showerror(UI[self.lang]['export_failed'], UI[self.lang]['export_failed'], parent=window)
        row = tk.Frame(window, bg=self.BG)
        row.pack(fill='x', padx=24, pady=20)
        tk.Button(row, text=UI[self.lang]['export_archive'], command=export_all, bg=self.ACCENT,
                  fg=self.BG, relief='flat', padx=20, pady=10).pack(side='left')
        tk.Button(row, text=UI[self.lang]['delete'], command=delete, bg=self.CARD,
                  fg=self.FG, relief='flat', padx=20, pady=10).pack(side='right')

    def callback_error(self, error_type, error, trace):
        # Do not put user input or sharing tokens in logs.
        logging.error('UI callback failed (%s)', error_type.__name__)
        self.cancel()
        messagebox.showerror('GhostTrack', UI[self.lang]['network_error'], parent=self.root)

    def close(self):
        self.closed = True
        self.cancel_event.set()
        self.job_id += 1
        self.store.settings.update(language=self.lang, region=self.region.get())
        self.store.save()
        self.root.destroy()

    def export(self):
        if not self.result:
            messagebox.showinfo(UI[self.lang]['info'], UI[self.lang]['first'])
            return
        path = filedialog.asksaveasfilename(defaultextension='.json',
                    initialfile=f'GhostTrack-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json',
                    filetypes=[('JSON', '*.json'), ('CSV', '*.csv'), ('HTML report', '*.html')])
        if not path:
            return
        data = self.localized_result()
        try:
            write_report(path, data, (UI[self.lang]['field'], UI[self.lang]['value']))
            self.set_state('saved')
        except OSError:
            messagebox.showerror(UI[self.lang]['export_failed'], UI[self.lang]['export_failed'])


if __name__ == '__main__':
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
    window = tk.Tk()
    app = App(window)
    try:
        app.store.directory.mkdir(parents=True, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(app.store.directory / 'application.log', maxBytes=200_000,
                                       backupCount=1, encoding='utf-8')
        logging.basicConfig(level=logging.WARNING, handlers=[handler],
                            format='%(asctime)s %(levelname)s %(message)s')
    except OSError:
        pass
    window.mainloop()
