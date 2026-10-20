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
from reports import write_report
from platforms import detect_platform, ProfileInputError, QueryCancelled
from datetime import datetime, timezone
from pathlib import Path
import logging
import sys




from i18n import LANGUAGES, UI, localize, platform_name


class App:
    BG, PANEL, CARD = '#0b1020', '#11192d', '#18233b'
    FG, MUTED, ACCENT = '#edf3ff', '#a6b5d2', '#5ee0bc'
    MODES = ['IP 归属地', '本机公网 IP', '号码归属地', '用户名链接', '国内平台']
    MODE_KEYS = ['ip', 'self', 'phone', 'username', 'domestic']

    def __init__(self, root, data_dir=None):
        self.root, self.result = root, {}
        self.store = Store(data_dir)
        self.events = queue.Queue()
        self.lang, self.mode, self.busy = self.store.settings['language'], 0, False
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
                              ('selectBackground', '#245565'), ('selectForeground', self.FG),
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
                        foreground=self.FG, rowheight=44, borderwidth=0, bordercolor=self.PANEL,
                        lightcolor=self.PANEL, darkcolor=self.PANEL, font=('Microsoft YaHei UI', 10))
        style.configure('Result.Treeview.Heading', background=self.CARD, foreground=self.MUTED,
                        bordercolor=self.PANEL, lightcolor=self.PANEL, darkcolor=self.PANEL,
                        padding=12, font=('Microsoft YaHei UI', 10))
        style.configure('Result.Vertical.TScrollbar', background=self.CARD, troughcolor=self.PANEL,
                         arrowcolor=self.ACCENT, borderwidth=0)
        style.map('Result.Treeview', background=[('selected', '#245565')])
        style.configure('Query.Horizontal.TProgressbar', background=self.ACCENT,
                         troughcolor=self.PANEL, borderwidth=0, thickness=4)
        side = tk.Frame(root, bg=self.PANEL, width=int(245 * self.scale))
        side.pack(side='left', fill='y')
        side.pack_propagate(False)
        self.brand = tk.Label(side, text='GHOST / TRACK', bg=self.PANEL, fg=self.ACCENT,
                              font=('Segoe UI', 17, 'bold'))
        self.brand.pack(anchor='w', padx=22, pady=(25, 4))
        tk.Label(side, text=f'DESKTOP EDITION   /   {VERSION}', bg=self.PANEL,
                 fg=self.MUTED, font=('Segoe UI', 9)).pack(anchor='w', padx=22, pady=(0, 25))
        self.label(side, 'tools', bg=self.PANEL).pack(anchor='w', padx=22, pady=(0, 12))
        self.nav = []
        for index, key in enumerate(self.MODE_KEYS):
            button = self.button_widget(side, key, lambda n=index: self.select(n))
            button.pack(fill='x', padx=14, pady=5)
            self.nav.append(button)
        tk.Frame(side, height=1, bg='#28354e').pack(fill='x', padx=22, pady=18)
        for key, command in (('history', self.history_dialog), ('settings', self.settings_dialog), ('help', self.help_dialog)):
            self.button_widget(side, key, command).pack(fill='x', padx=14, pady=4)
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
        self.heading = self.label(main, 'tagline', size=22, color=self.FG, wraplength=730)
        self.heading.grid(row=1, column=0, sticky='w', pady=(14, 18))
        form = tk.Frame(main, bg=self.PANEL, padx=22, pady=18)
        form.grid(row=2, column=0, sticky='ew')
        self.label(form, 'parameters', bg=self.PANEL, color=self.ACCENT).pack(anchor='w')
        self.label(form, 'input', bg=self.PANEL).pack(anchor='w', pady=(14, 6))
        input_row = tk.Frame(form, bg=self.PANEL)
        input_row.pack(fill='x')
        self.entry = tk.Entry(input_row, textvariable=self.value, bg=self.CARD, fg=self.FG,
                              disabledbackground=self.CARD, disabledforeground=self.MUTED,
                              insertbackground=self.ACCENT, relief='flat', font=('Segoe UI', 14))
        self.entry.pack(side='left', fill='x', expand=True, ipady=10)
        self.button_widget(input_row, 'paste', self.paste).pack(side='right', padx=(8, 0))
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
        self.platform_box = ttk.Combobox(row, textvariable=self.platform_choice, state='readonly', width=22)
        self.platform_box.bind('<<ComboboxSelected>>', self.choose_platform)
        self.button = self.button_widget(row, 'run', self.start, primary=True)
        self.button.pack(side='right')
        self.cancel_button = self.button_widget(row, 'cancel', self.cancel)
        self.cancel_button.pack(side='right', padx=8)
        self.cancel_button.config(state='disabled')
        results_header = tk.Frame(main, bg=self.BG)
        results_header.grid(row=3, column=0, sticky='ew', pady=(24, 12))
        self.label(results_header, 'results', color=self.FG, size=12).pack(side='left')
        self.progress = ttk.Progressbar(results_header, mode='indeterminate', length=70,
                                        style='Query.Horizontal.TProgressbar')
        self.filter_entry = tk.Entry(results_header, textvariable=self.filter, bg=self.CARD, fg=self.FG,
                                      insertbackground=self.ACCENT, relief='flat', width=22,
                                      font=('Microsoft YaHei UI', 10))
        self.filter_entry.pack(side='right', ipady=5)
        self.label(results_header, 'filter', size=8, wraplength=220).pack(side='right', padx=8)
        self.filter.trace_add('write', lambda *_: self.show_result() if self.result else None)
        self.filter_entry.bind('<Escape>', lambda _: self.filter.set(''))
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
        self.scroll = ttk.Scrollbar(results, command=self.tree.yview, style='Result.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=self.scroll.set)
        self.tree.bind('<<TreeviewSelect>>', self.select_result)
        self.tree.bind('<Control-c>', self.copy_selected)
        self.tree.bind('<Control-C>', self.copy_selected)
        self.tree.bind('<Double-1>', self.copy_selected)
        self.detail = tk.Text(main, bg=self.PANEL, fg=self.MUTED, height=3, state='disabled',
                              wrap='word', relief='flat', padx=10, pady=8, font=('Microsoft YaHei UI', 9))
        self.detail.grid(row=5, column=0, sticky='ew', pady=(8, 0))
        self.detail.grid_remove()
        self.status_label = tk.Label(main, textvariable=self.status, bg=self.BG, fg=self.ACCENT,
                                     font=('Microsoft YaHei UI', 10), anchor='w', justify='left')
        self.status_label.grid(row=6, column=0, sticky='ew', pady=(6, 0))
        actions = tk.Frame(main, bg=self.BG)
        actions.grid(row=7, column=0, sticky='ew', pady=(10, 10))
        self.action_buttons = []
        for key, command in (('copy_selected', self.copy_selected), ('copy', self.copy),
                             ('open_profile', self.open_profile), ('export', self.export)):
            widget = self.button_widget(actions, key, command)
            widget.pack(side='left', padx=(0, 8))
            self.action_buttons.append(widget)
        self.notice = self.label(main, 'notice', wraplength=740)
        self.notice.grid(row=8, column=0, sticky='w')
        def resize(event):
            width = max(200, event.width - 44)
            for widget in (self.heading, self.hint, self.notice, self.empty_help, self.status_label):
                widget.config(wraplength=width)
        main.bind('<Configure>', resize)
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
        self.store.settings['language'] = self.lang
        if not self.store.save():
            self.status.set(UI[self.lang]['state_warning'])

    def refresh_language(self):
        for widget, key in self.bindings:
            widget.config(text=UI[self.lang][key])
        self.tree.heading('key', text=UI[self.lang]['field'], anchor='w')
        self.tree.heading('value', text=UI[self.lang]['value'], anchor='w')
        self.status.set(UI[self.lang][self.state])
        self.filter_entry.config(takefocus=True)
        self.select(self.mode)
        if self.result:
            self.show_result()
        elif self.state == 'failed':
            self.empty_title.config(text=UI[self.lang]['failed'])
            self.empty_help.config(text=UI[self.lang][self.error_key])
        elif self.busy:
            self.show_empty('busy', 'empty_help')

    def select(self, index):
        if self.busy and index != self.mode:
            self.cancel()
        self.mode = index
        self.platform_choice.set(platform_name(self.platform.get(), self.lang))
        self.platform_box.config(values=[platform_name(p, self.lang) for p in ('Auto', *PLATFORMS)])
        for n, button in enumerate(self.nav):
            button.config(bg='#21473f' if n == index else self.CARD,
                          fg=self.ACCENT if n == index else self.FG)
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
            self.region_label.pack(side='left', padx=(0, 8))
            self.region_box.pack(side='left')

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
        self.button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.entry.config(state='disabled')
        self.platform_box.config(state='disabled')
        self.set_state('busy')
        self.progress.pack(side='left', padx=12)
        self.progress.start(15)
        self.result = {}
        self.filter.set('')
        self.update_actions()
        self.show_empty('busy', 'empty_help')
        def work():
            try:
                data = query(*args, cancel=cancel)
                data.setdefault('查询时间 UTC', datetime.now(timezone.utc).isoformat(timespec='seconds'))
                data['查询工具'] = args[0]
                data['查询输入'] = args[1] if args[0] != '本机公网 IP' else '—'
                if not cancel.is_set():
                    self.events.put((job_id, True, data, args))
            except QueryCancelled:
                pass
            except ProfileInputError as error:
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
        try:
            job_id, success, data, args = self.events.get_nowait()
            if job_id != self.job_id:
                self.root.after(100, self.poll)
                return
            self.busy = False
            self.progress.stop()
            self.progress.pack_forget()
            self.button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.select(self.mode)
            if success:
                self.result = data
                self.show_result()
                limited = data.get('页面状态') and '已读取页面元信息' not in data['页面状态']
                self.set_state('limited' if limited else 'done')
                if args and not self.store.record(args[0], args[1], args[2], args[4], data):
                    self.status.set(UI[self.lang]['state_warning'])
            else:
                self.error_key = data
                self.set_state('failed')
                self.show_empty('failed', data)
            self.update_actions()
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def cancel(self):
        if not self.busy:
            return
        self.cancel_event.set()
        self.job_id += 1
        self.busy = False
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
        self.action_buttons[2].config(state='normal' if self.result.get('主页链接') else 'disabled')

    def show_empty(self, title, help_key):
        self.set_detail('')
        self.detail.grid_remove()
        self.tree.pack_forget()
        self.scroll.pack_forget()
        self.empty.pack(fill='both', expand=True)
        self.empty_title.config(text=UI[self.lang][title])
        self.empty_help.config(text=UI[self.lang][help_key])

    def localized_result(self):
        return {localize(k, self.lang): localize(v, self.lang) for k, v in self.result.items()}

    def show_result(self):
        self.set_detail(UI[self.lang]['select_row'])
        self.detail.grid()
        self.empty.pack_forget()
        self.scroll.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.delete(*self.tree.get_children())
        needle = self.filter.get().casefold().strip()
        for key, value in self.localized_result().items():
            if not needle or needle in f'{key} {value}'.casefold():
                self.tree.insert('', 'end', values=(key, value))

    def select_result(self, _=None):
        selected = self.tree.selection()
        if selected:
            key, value = self.tree.item(selected[0], 'values')
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
        try:
            if detect_platform(url):
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
                             selectbackground='#245565', font=('Microsoft YaHei UI', 10),
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
            limited = self.result.get('页面状态') and '已读取页面元信息' not in self.result['页面状态']
            self.set_state('limited' if limited else 'done')
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
