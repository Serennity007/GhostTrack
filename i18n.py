"""Complete desktop translations; canonical query fields remain stable internally."""
LANGUAGES = {'简体中文': 'zh', 'English': 'en', '日本語': 'ja', 'Español': 'es'}
TEXT = {
'zh': ['信息探索工作台', '从公开信息到清晰结果', '查询工具', 'IP 归属地', '本机公网 IP', '号码归属地', '用户名链接', '查询参数', '输入 IP、电话号码或用户名', '号码默认地区', '开始查询', '查询结果', '复制结果', '导出结果', '就绪', '查询中…', '查询完成', '查询失败', '导出完成', '已复制', '请先完成查询', '提示', '字段', '值', '公开数据 · 尊重隐私', '归属地是估算或号码段信息，不代表实时位置。', '输入公网 IPv4 / IPv6 地址', '无需输入，查询当前网络的公网 IP', '建议输入含国家区号的号码，例如 +86…', '生成主页链接，账号存在与身份需自行核实', '等待你的第一次查询', '选择左侧工具，输入信息后开始查询。', '导出失败', '网络或服务异常，请稍后重试。', '请输入有效的 IP、号码或用户名。'],
'en': ['Information workspace', 'Turn public information into clear results', 'TOOLS', 'IP location', 'My public IP', 'Phone metadata', 'Username links', 'QUERY PARAMETERS', 'IP, phone number or username', 'Default phone region', 'Run query', 'RESULTS', 'Copy results', 'Export results', 'Ready', 'Querying…', 'Query complete', 'Query failed', 'Export complete', 'Copied', 'Run a query first', 'Information', 'Field', 'Value', 'Public data · Respect privacy', 'Locations are estimates or numbering metadata, never live tracking.', 'Enter a public IPv4 / IPv6 address', 'No input needed: check your current public IP', 'Include the country calling code, e.g. +1…', 'Generate profile links; existence and identity are unverified', 'Your next discovery starts here', 'Choose a tool, enter a value and run your query.', 'Export failed', 'Network or service error. Please try again later.', 'Enter a valid IP address, phone number or username.'],
'ja': ['情報ワークスペース', '公開情報を、わかりやすい結果へ', 'ツール', 'IP の地域', '自分の公開 IP', '電話番号情報', 'ユーザー名リンク', '検索条件', 'IP・電話番号・ユーザー名', '電話番号の既定地域', '検索する', '検索結果', '結果をコピー', '結果を保存', '準備完了', '検索中…', '検索完了', '検索失敗', '保存完了', 'コピーしました', '先に検索を実行してください', 'お知らせ', '項目', '値', '公開データ · プライバシーを尊重', '地域は推定値または番号帯の情報であり、現在地ではありません。', '公開 IPv4 / IPv6 アドレスを入力', '入力不要：現在の公開 IP を確認', '国番号付きの入力を推奨します（例：+81…）', 'プロフィールへのリンクを生成。存在・本人確認は未実施', '最初の検索を始めましょう', '左のツールを選び、情報を入力して検索します。', '保存に失敗しました', '通信またはサービスのエラーです。後でもう一度お試しください。', '有効な IP・電話番号・ユーザー名を入力してください。'],
'es': ['Espacio de información', 'Información pública, resultados claros', 'HERRAMIENTAS', 'Ubicación de IP', 'Mi IP pública', 'Datos de teléfono', 'Enlaces de usuario', 'PARÁMETROS', 'IP, teléfono o nombre de usuario', 'Región del teléfono', 'Consultar', 'RESULTADOS', 'Copiar resultados', 'Exportar resultados', 'Listo', 'Consultando…', 'Consulta completada', 'Error en la consulta', 'Exportación completada', 'Copiado', 'Realiza una consulta primero', 'Información', 'Campo', 'Valor', 'Datos públicos · Respeta la privacidad', 'Las ubicaciones son estimaciones o datos de numeración, nunca rastreo en vivo.', 'Introduce una dirección IPv4 / IPv6 pública', 'Sin entrada: consulta tu IP pública actual', 'Incluye el código de país, por ejemplo +34…', 'Genera enlaces; la existencia y la identidad no están verificadas', 'Tu próxima consulta empieza aquí', 'Elige una herramienta, introduce un dato y consulta.', 'Error al exportar', 'Error de red o del servicio. Inténtalo más tarde.', 'Introduce una IP, un teléfono o un usuario válido.']}
KEYS = ['workspace','tagline','tools','ip','self','phone','username','parameters','input','region','run','results','copy','export','ready','busy','done','failed','saved','copied','first','info','field','value','privacy','notice','hint_ip','hint_self','hint_phone','hint_username','empty','empty_help','export_failed','network_error','input_error']
EXTRA_KEYS = ['domestic', 'hint_domestic', 'platform', 'hint_uid', 'hint_slug',
              'copy_selected', 'open_profile', 'select_row', 'no_profile']
EXTRA = {
    'zh': ['国内平台', '查询国内平台公开主页', '平台', '输入数字 UID 或完整 HTTPS 主页链接（不支持昵称反查）', '输入主页标识或完整 HTTPS 主页链接（不支持昵称反查）', '复制选中值', '打开主页', '请先选中一条结果；双击或 Ctrl+C 可复制', '当前结果没有主页链接'],
    'en': ['Chinese platforms', 'Look up public profiles on Chinese platforms', 'Platform', 'Numeric UID or full HTTPS profile URL; display names are not supported', 'Profile identifier or full HTTPS profile URL; display names are not supported', 'Copy value', 'Open profile', 'Select a result first; double-click or Ctrl+C to copy', 'No profile link in the current result'],
    'ja': ['中国のプラットフォーム', '中国の公開プロフィールを検索', 'サービス', '数値 UID または HTTPS プロフィール URL（表示名からの検索は非対応）', 'プロフィール ID または HTTPS URL（表示名からの検索は非対応）', '選択値をコピー', 'ページを開く', '行を選択してください。ダブルクリックまたは Ctrl+C でコピー', '現在の結果にプロフィールリンクはありません'],
    'es': ['Plataformas chinas', 'Consulta perfiles públicos de plataformas chinas', 'Plataforma', 'UID numérico o URL HTTPS del perfil; no admite nombres visibles', 'Identificador o URL HTTPS del perfil; no admite nombres visibles', 'Copiar valor', 'Abrir perfil', 'Selecciona una fila; doble clic o Ctrl+C para copiar', 'El resultado actual no tiene enlace de perfil'],
}
KEYS += EXTRA_KEYS
for language, values in TEXT.items():
    values.extend(EXTRA[language])
UI = {lang: dict(zip(KEYS, values)) for lang, values in TEXT.items()}
UI['zh']['copy'] = '复制全部'
UI['en']['copy'] = 'Copy all'
UI['ja']['copy'] = 'すべてコピー'
UI['es']['copy'] = 'Copiar todo'
FIELDS = {
'国际格式': ['International format','国際形式','Formato internacional'], '归属地': ['Numbering region','番号の地域','Región de numeración'], '运营商': ['Carrier','通信事業者','Operador'], '地区代码': ['Region code','地域コード','Código de región'], '时区': ['Time zone','タイムゾーン','Zona horaria'], '有效号码': ['Valid number','有効な番号','Número válido'], '说明': ['Notes','補足','Notas'], '公网 IP': ['Public IP','公開 IP','IP pública'], '国家': ['Country','国','País'], '地区': ['Region','地域','Región'], '城市': ['City','都市','Ciudad'], '纬度': ['Latitude','緯度','Latitud'], '经度': ['Longitude','経度','Longitud'], '网络服务商': ['Internet provider','プロバイダー','Proveedor de Internet'],
'号码段元数据，不代表持有人身份或实时位置': ['Numbering metadata; does not identify a person or live location','番号帯の情報です。本人や現在地を示すものではありません','Datos de numeración; no identifican a una persona ni su ubicación actual'],
'仅生成公开主页链接；未核实账号存在或身份归属': ['Public profile links only; account existence and identity are unverified','公開プロフィールのリンクのみ。アカウントの存在・本人確認は未実施','Solo enlaces públicos; existencia e identidad sin verificar'],
'IP 数据库估算位置，不代表设备实时位置': ['Estimated database location; not a live device location','データベースによる推定地域であり、端末の現在地ではありません','Ubicación estimada de la base de datos; no es la ubicación en vivo']}
FIELDS.update({
    '平台': ['Platform', 'サービス', 'Plataforma'],
    '主页链接': ['Profile URL', 'プロフィール URL', 'URL del perfil'],
    '查询时间 UTC': ['Queried at (UTC)', '検索日時 (UTC)', 'Fecha de consulta (UTC)'],
    'HTTP 状态': ['HTTP status', 'HTTP ステータス', 'Estado HTTP'],
    '页面状态': ['Page status', 'ページの状態', 'Estado de la página'],
    '页面标题': ['Page title', 'ページタイトル', 'Título de la página'],
    '公开简介': ['Public description', '公開の説明', 'Descripción pública'],
    '仅查询公开页面；未核实账号存在或身份归属': ['Public pages only; account existence and identity are unverified', '公開ページのみ。アカウントの存在・本人確認は未実施', 'Solo páginas públicas; existencia e identidad sin verificar'],
    '页面未找到；无法确认账号是否存在': ['Page not found; account existence is unknown', 'ページが見つかりません。アカウントの存在は不明です', 'Página no encontrada; se desconoce si la cuenta existe'],
    '访问受限或发生跳转；账号状态未知': ['Access restricted or redirected; account status unknown', 'アクセス制限または転送。アカウントの状態は不明です', 'Acceso restringido o redirección; estado de cuenta desconocido'],
    '未返回可解析的公开 HTML；账号状态未知': ['No parseable public HTML; account status unknown', '解析可能な公開 HTML がありません。アカウントの状態は不明です', 'No hay HTML público analizable; estado de cuenta desconocido'],
    '需要登录或验证；账号状态未知': ['Login or verification required; account status unknown', 'ログインまたは認証が必要です。アカウントの状態は不明です', 'Se requiere inicio de sesión o verificación; estado desconocido'],
    '已读取页面元信息；账号存在与身份仍未核实': ['Page metadata read; account existence and identity remain unverified', 'ページ情報を取得。アカウントの存在・本人確認は未実施', 'Metadatos obtenidos; existencia e identidad sin verificar'],
    '页面需脚本加载或未提供元信息；账号状态未知': ['Page requires scripts or has no metadata; account status unknown', 'スクリプトが必要、または情報がありません。アカウントの状態は不明です', 'La página requiere scripts o no tiene metadatos; estado desconocido'],
    '网络异常；请在浏览器中打开主页链接': ['Network error; open the profile URL in your browser', '通信エラー。ブラウザーでプロフィール URL を開いてください', 'Error de red; abre la URL del perfil en el navegador'],
})

PRODUCT = {
    'paste': ['粘贴', 'Paste', '貼り付け', 'Pegar'],
    'clipboard_empty': ['剪贴板没有可粘贴的文本', 'No text in the clipboard', 'クリップボードにテキストがありません', 'No hay texto en el portapapeles'],
    'history': ['查询历史', 'History', '履歴', 'Historial'],
    'settings': ['设置', 'Settings', '設定', 'Ajustes'],
    'help': ['使用帮助', 'Help', 'ヘルプ', 'Ayuda'],
    'cancel': ['取消', 'Cancel', '中止', 'Cancelar'],
    'cancelled': ['已取消，未保存结果', 'Cancelled; no result saved', '中止しました。結果は未保存です', 'Cancelado; resultado no guardado'],
    'filter': ['筛选结果字段或内容', 'Filter fields or values', '項目・内容を絞り込み', 'Filtrar campos o valores'],
    'restore': ['查看结果', 'View result', '結果を表示', 'Ver resultado'],
    'clear_history': ['清空历史', 'Clear history', '履歴を消去', 'Borrar historial'],
    'clear_confirm': ['清空全部本地查询历史？此操作无法撤销。', 'Clear all local query history? This cannot be undone.', 'ローカル履歴をすべて消去しますか？元に戻せません。', '¿Borrar todo el historial local? No se puede deshacer.'],
    'remember': ['重启后保留查询历史（仅保存在本机）', 'Keep history between sessions (stored locally)', '再起動後も履歴を保持（この端末のみ）', 'Conservar historial entre sesiones (solo local)'],
    'remember_help': ['默认仅保留本次会话。启用后最多保存 50 条，含输入、分享链接和查询结果；可随时清空。', 'Session-only by default. When enabled, up to 50 inputs, share links and results are stored locally. Clear them anytime.', '既定では今回のセッションのみ。オンにすると入力・共有リンク・結果を最大50件保存します。いつでも消去できます。', 'Solo la sesión actual por defecto. Al activarlo se guardan hasta 50 entradas, enlaces y resultados. Puedes borrarlos.'],
    'save': ['保存设置', 'Save settings', '設定を保存', 'Guardar ajustes'],
    'close': ['关闭', 'Close', '閉じる', 'Cerrar'],
    'state_warning': ['无法读写本地设置；本次会话仍可继续使用', 'Local settings unavailable; this session can continue', 'ローカル設定を利用できません。今回の操作は続行できます', 'Ajustes locales no disponibles; puedes seguir usando la sesión'],
    'thread_wait': ['前一次网络请求仍在结束，请稍后再试', 'Previous requests are finishing; please retry shortly', '前の通信が終了するまで少し待って再試行してください', 'Las solicitudes anteriores están terminando; inténtalo en breve'],
    'saved_settings': ['设置已保存', 'Settings saved', '設定を保存しました', 'Ajustes guardados'],
    'no_history': ['暂无历史记录', 'No history yet', '履歴はありません', 'Todavía no hay historial'],
    'limited': ['页面受限或信息不足，可打开主页核实', 'Limited page data; open the profile to verify', 'ページ情報が制限されています。ブラウザーで確認してください', 'Datos limitados; abre el perfil para comprobar'],
    'one_link': ['一次只粘贴一个主页链接或分享文案', 'Paste one profile link or share message at a time', 'プロフィールリンク・共有文は一度に1件入力してください', 'Pega un solo enlace de perfil o mensaje compartido'],
    'unsupported_platform': ['此链接暂不支持，请使用列表中平台的公开主页', 'Unsupported link; use a public profile from a listed platform', '非対応リンクです。対応サービスの公開プロフィールを入力してください', 'Enlace no compatible; usa un perfil público de una plataforma de la lista'],
    'choose_platform': ['仅输入 ID 时，请先选择具体平台', 'Select a platform when entering an ID without a URL', 'ID のみの場合はサービスを選択してください', 'Selecciona una plataforma al introducir solo un ID'],
    'profile_only': ['请粘贴个人主页链接；视频、笔记、登录页暂不支持', 'Use a profile link; videos, posts and login pages are not supported', 'プロフィールリンクを入力してください。動画・投稿・ログインページは非対応です', 'Usa un enlace de perfil; no se admiten vídeos, publicaciones ni páginas de acceso'],
    'profile_input': ['主页 ID 格式不正确。抖音请用主页链接，不能直接用抖音号；小红书用户 ID 为 24 位十六进制。', 'Invalid profile ID. For Douyin use a profile URL, not a display handle. Xiaohongshu IDs contain 24 hexadecimal characters.', 'ID の形式が無効です。抖音は表示IDではなくプロフィール URL、小紅書は24桁の16進IDを使用してください。', 'ID no válido. Para Douyin usa la URL del perfil, no el alias. Los ID de Xiaohongshu tienen 24 caracteres hexadecimales.'],
    'short_link_failed': ['分享短链未能展开，请在浏览器打开后复制完整主页地址', 'Could not expand the share link; open it in a browser and copy the full profile URL', '短縮リンクを展開できません。ブラウザーで開いて完全なプロフィール URL をコピーしてください', 'No se pudo resolver el enlace corto; ábrelo en el navegador y copia la URL completa del perfil'],
    'unsafe_redirect': ['分享链接跳转到非所选平台，已停止访问', 'Share link left the selected platform; stopped', '共有リンクが別のサービスへ移動したため停止しました', 'El enlace salió de la plataforma seleccionada; se detuvo'],
    'auto': ['自动识别链接', 'Auto-detect URL', 'URL を自動判定', 'Detectar URL'],
    'hint_share': ['粘贴主页链接或完整分享文案；支持抖音/小红书主页短链。ID 查询需选择平台。', 'Paste a profile URL or share message. Douyin/Xiaohongshu profile short links are supported. Select a platform for bare IDs.', 'プロフィール URL・共有文を貼り付け。抖音/小紅書の短縮リンク対応。ID の場合はサービスを選択。', 'Pega una URL de perfil o un mensaje compartido. Admite enlaces cortos de Douyin/Xiaohongshu. Para ID, elige plataforma.'],
    'history_title': ['最近查询 · 最多 50 条', 'Recent queries · up to 50', '最近の検索 · 最大50件', 'Consultas recientes · hasta 50'],
    'help_body': ['1. 选择工具，输入内容，按 Enter 查询。\n2. 国内平台支持抖音、小红书、快手、B站、微博、知乎、豆瓣。粘贴主页链接会自动识别平台；不支持按昵称确认身份。\n3. 抖音主页 /user/…，小红书主页 /user/profile/…，快手主页 /profile/…。视频/笔记分享不是主页。\n4. 选中结果行后 Ctrl+C 或双击复制该值；可复制全部、打开主页，或导出 JSON / CSV / HTML 报告。\n5. Esc 取消查询；Ctrl+L 聚焦输入。取消后迟到的响应不会覆盖新结果。\n6. 历史默认仅保留当前会话，设置中可开启本机持久化。语言选择自动记忆。\n\n平台要求登录、验证或脚本运行时，仅能保留链接和访问状态。号码归属地/IP 位置不代表实时位置。',
                  '1. Choose a tool, enter a value and press Enter.\n2. Profiles: Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu and Douban. URLs auto-detect the platform; display names do not establish identity.\n3. Use /user/… on Douyin, /user/profile/… on Xiaohongshu, /profile/… on Kuaishou. Video/post shares are not profiles.\n4. Ctrl+C or double-click a selected row to copy its value. Copy all, open the profile or export JSON/CSV/HTML.\n5. Esc cancels; Ctrl+L focuses input. Late cancelled responses cannot replace newer results.\n6. History is session-only by default; enable local persistence in Settings. Language is remembered.\n\nLogin, verification and JavaScript pages may expose only a link and access status. Phone/IP regions are not live locations.',
                  '1. ツールを選択し入力後 Enter で検索。\n2. 抖音、小紅書、快手、Bilibili、Weibo、知乎、豆瓣に対応。URL でサービスを自動判定。表示名での本人確認はできません。\n3. プロフィール URL を使用してください。動画・投稿の共有は非対応です。\n4. 行を選択して Ctrl+C またはダブルクリックで値をコピー。全結果のコピー、ページを開く、JSON/CSV/HTML の保存も可能。\n5. Esc で中止、Ctrl+L で入力欄へ。中止した応答は新しい結果を上書きしません。\n6. 履歴は既定でセッションのみ。設定でローカル保存を有効にできます。言語は記憶されます。\n\nログイン・認証・JavaScript が必要なページはリンクと状態のみの場合があります。番号・IP の地域は現在地ではありません。',
                  '1. Elige herramienta, introduce un dato y pulsa Enter.\n2. Perfiles: Douyin, Xiaohongshu, Kuaishou, Bilibili, Weibo, Zhihu y Douban. La URL detecta la plataforma; los alias no confirman identidad.\n3. Usa enlaces de perfil, no enlaces de vídeos o publicaciones.\n4. Ctrl+C o doble clic copia el valor seleccionado. También puedes copiar todo, abrir el perfil y exportar JSON/CSV/HTML.\n5. Esc cancela; Ctrl+L enfoca la entrada. Las respuestas canceladas no sobrescriben nuevos resultados.\n6. Historial solo de la sesión por defecto; activa la persistencia local en Ajustes. El idioma se recuerda.\n\nLas páginas con acceso, verificación o JavaScript pueden mostrar solo enlace y estado. Las regiones de teléfono/IP no son ubicaciones en vivo.'],
    'releases': ['下载与版本记录', 'Downloads & releases', 'ダウンロード・更新履歴', 'Descargas y versiones'],
}
for key, translations in PRODUCT.items():
    KEYS.append(key)
    for language, value in zip(('zh', 'en', 'ja', 'es'), translations):
        UI[language][key] = value
FIELDS.update({
    '查询工具': ['Query tool', '検索ツール', 'Herramienta'],
    '返回平台通用页面，未取得用户资料': ['Generic platform page; no user profile data obtained', 'サービスの共通ページです。ユーザー情報は取得できませんでした', 'Página genérica; no se obtuvieron datos del perfil'],
    '查询输入': ['Query input', '検索入力', 'Entrada de consulta'],
    'IP 归属地': [UI['en']['ip'], UI['ja']['ip'], UI['es']['ip']],
    '本机公网 IP': [UI['en']['self'], UI['ja']['self'], UI['es']['self']],
    '号码归属地': [UI['en']['phone'], UI['ja']['phone'], UI['es']['phone']],
    '用户名链接': [UI['en']['username'], UI['ja']['username'], UI['es']['username']],
    '国内平台': [UI['en']['domestic'], UI['ja']['domestic'], UI['es']['domestic']],
})

PLATFORM_NAMES = {
    'Douyin': ['抖音', 'Douyin', '抖音 (Douyin)', 'Douyin'],
    'Xiaohongshu': ['小红书', 'Xiaohongshu / RedNote', '小紅書 (RedNote)', 'Xiaohongshu / RedNote'],
    'Kuaishou': ['快手', 'Kuaishou', '快手 (Kuaishou)', 'Kuaishou'],
    'Bilibili': ['B站', 'Bilibili', 'Bilibili', 'Bilibili'],
    'Weibo': ['微博', 'Weibo', 'Weibo', 'Weibo'],
    'Zhihu': ['知乎', 'Zhihu', '知乎 (Zhihu)', 'Zhihu'],
    'Douban': ['豆瓣', 'Douban', '豆瓣 (Douban)', 'Douban'],
}


def platform_name(platform, lang):
    if platform == 'Auto':
        return UI[lang]['auto']
    return PLATFORM_NAMES.get(platform, [platform] * 4)[('zh', 'en', 'ja', 'es').index(lang)]


def localize(value, lang):
    if isinstance(value, bool):
        return {'zh': ('否','是'), 'en': ('No','Yes'), 'ja': ('いいえ','はい'), 'es': ('No','Sí')}[lang][value]
    if value is None:
        return '—'
    if lang == 'zh' or value not in FIELDS:
        return value
    return FIELDS[value][{'en':0,'ja':1,'es':2}[lang]]


PUBLIC_UI = {
    'domain': ['域名档案', 'Domain registry', 'ドメイン登録情報', 'Registro de dominio'],
    'dns': ['DNS 记录', 'DNS records', 'DNS レコード', 'Registros DNS'],
    'website': ['网站与证书', 'Website + TLS', 'ウェブ・TLS 証明書', 'Web y certificado TLS'],
    'network': ['IP / ASN 注册', 'IP / ASN registry', 'IP / ASN 登録情報', 'Registro de IP / ASN'],
    'github': ['GitHub 公开资料', 'GitHub profile', 'GitHub 公開情報', 'Perfil de GitHub'],
    'hint_domain': ['输入域名，例如 example.com；查询注册商、注册时间、到期时间和名称服务器。', 'Domain, e.g. example.com: registrar, registration dates and nameservers.', 'ドメイン名（例 example.com）：登録事業者・登録日時・有効期限・ネームサーバー。', 'Dominio, p. ej. example.com: registrador, fechas y servidores de nombres.'],
    'hint_dns': ['输入域名；并行查询 A / AAAA / CNAME / MX / NS / TXT / SOA / CAA。', 'Domain: A / AAAA / CNAME / MX / NS / TXT / SOA / CAA records.', 'ドメイン名：A / AAAA / CNAME / MX / NS / TXT / SOA / CAA を検索。', 'Dominio: registros A / AAAA / CNAME / MX / NS / TXT / SOA / CAA.'],
    'hint_website': ['输入域名或 HTTPS 网址；查看响应、跳转、公开响应头和 TLS 证书。', 'Domain or HTTPS URL: response, redirects, public headers and TLS certificate.', 'ドメイン名・HTTPS URL：応答・転送・公開ヘッダー・TLS 証明書。', 'Dominio o URL HTTPS: respuesta, redirecciones, cabeceras y certificado TLS.'],
    'hint_network': ['输入公网 IPv4 / IPv6 或 AS15169；查看注册网段、CIDR、网络名称和国家代码。', 'Public IPv4 / IPv6 or AS15169: registered range, CIDR, network name and country code.', '公開 IPv4 / IPv6・AS15169：登録範囲・CIDR・ネットワーク名・国コード。', 'IPv4 / IPv6 pública o AS15169: rango, CIDR, nombre de red y país.'],
    'invalid_asn': ['请输入有效 ASN，例如 AS15169', 'Enter a valid ASN, e.g. AS15169', '有効な ASN を入力してください（例 AS15169）', 'Introduce un ASN válido, p. ej. AS15169'],
    'hint_github': ['输入 GitHub 用户名或主页链接；公开简介、仓库数和最近 5 个公开仓库。', 'GitHub username or profile URL: public bio, counts and 5 recent repositories.', 'GitHub ユーザー名・URL：公開紹介文・件数・最近の公開リポジトリ5件。', 'Usuario o URL de GitHub: biografía, estadísticas y 5 repositorios recientes.'],
    'invalid_domain': ['请输入有效的公网域名，例如 example.com', 'Enter a valid public domain, e.g. example.com', '公開ドメイン名を入力してください（例 example.com）', 'Introduce un dominio público válido, p. ej. example.com'],
    'public_not_found': ['公开来源未找到对应记录', 'No record found at the public source', '公開情報源にレコードがありません', 'No se encontró un registro público'],
    'public_rate_limit': ['公开服务限制了当前请求，请稍后重试', 'Public service denied or rate-limited this request; retry later', '公開サービスで制限されています。後で再試行してください', 'El servicio limitó la solicitud; inténtalo más tarde'],
    'source_unavailable': ['来源暂不可用、响应过大或超时，请稍后重试', 'Source unavailable, response too large or timed out', '情報源が利用不可・応答が大きすぎる・タイムアウトです', 'Fuente no disponible, respuesta demasiado grande o tiempo agotado'],
    'public_address_only': ['仅查询公网地址；域名不能解析到内网、回环或保留地址', 'Public addresses only; private, loopback and reserved targets are blocked', '公開アドレスのみ対応。プライベート・ループバック・予約アドレスは不可', 'Solo direcciones públicas; no se admiten destinos privados o reservados'],
    'invalid_github': ['请输入有效的 GitHub 用户名或账号主页链接', 'Enter a valid GitHub username or profile URL', '有効な GitHub ユーザー名・プロフィール URL を入力してください', 'Introduce un usuario o URL de perfil de GitHub válido'],
    'https_public_only': ['请输入公网 HTTPS 网址，仅支持默认 443 端口', 'Use a public HTTPS URL on the default port 443', '公開 HTTPS URL（既定ポート443）を入力してください', 'Usa una URL HTTPS pública en el puerto 443'],
    'tls_failed': ['TLS 证书验证或握手失败，未继续访问', 'TLS certificate validation or handshake failed; stopped', 'TLS 証明書検証・ハンドシェイクに失敗したため停止しました', 'Falló la validación o conexión TLS; se detuvo el acceso'],
    'redirect_limit': ['网站跳转次数超过限制，已停止访问', 'Redirect limit reached; stopped', '転送回数の上限に達したため停止しました', 'Se alcanzó el límite de redirecciones'],
}
for key, translations in PUBLIC_UI.items():
    KEYS.append(key)
    for language, value in zip(('zh', 'en', 'ja', 'es'), translations):
        UI[language][key] = value
for language, workspace, input_label, source_label in (
        ('zh', '公开信息控制台', '目标 / 域名 / IP / 用户名 / 主页链接', '打开来源'),
        ('en', 'PUBLIC DATA CONSOLE', 'Target / domain / IP / username / profile URL', 'Open source'),
        ('ja', '公開情報コンソール', '対象 / ドメイン / IP / ユーザー名 / URL', '情報源を開く'),
        ('es', 'CONSOLA DE DATOS PÚBLICOS', 'Destino / dominio / IP / usuario / URL', 'Abrir fuente')):
    UI[language].update(workspace=workspace, input=input_label, open_profile=source_label)

FIELDS.update({
    '国内格式': ['National format', '国内形式', 'Formato nacional'],
    'E.164 格式': ['E.164 format', 'E.164 形式', 'Formato E.164'],
    '国家呼叫码': ['Country calling code', '国番号', 'Código telefónico del país'],
    '可能有效': ['Possible number', '有効な可能性', 'Número posible'],
    '网络组织': ['Network organization', 'ネットワーク組織', 'Organización de red'],
    '网络域名': ['Network domain', 'ネットワークドメイン', 'Dominio de red'],
    '洲': ['Continent', '大陸', 'Continente'],
    '邮政编码': ['Postal code', '郵便番号', 'Código postal'],
    'ASN 起始': ['Start ASN', '開始 ASN', 'ASN inicial'],
    'ASN 结束': ['End ASN', '終了 ASN', 'ASN final'],
    'DNSSEC 已签名': ['DNSSEC delegation signed', 'DNSSEC 委任署名', 'Delegación DNSSEC firmada'],
    '来源链接': ['Source URL', '情報源 URL', 'URL de la fuente'],
    '域名': ['Domain', 'ドメイン', 'Dominio'],
    '注册状态': ['Registration status', '登録状態', 'Estado del registro'],
    '名称服务器': ['Nameservers', 'ネームサーバー', 'Servidores de nombres'],
    '注册商': ['Registrar', '登録事業者', 'Registrador'],
    '注册时间': ['Registered at', '登録日時', 'Fecha de registro'],
    '到期时间': ['Expires at', '有効期限', 'Fecha de vencimiento'],
    '更新时间': ['Updated at', '更新日時', 'Fecha de actualización'],
    '网络名称': ['Network name', 'ネットワーク名', 'Nombre de la red'],
    '网络标识': ['Network handle', 'ネットワーク識別子', 'Identificador de red'],
    '起始地址': ['Start address', '開始アドレス', 'Dirección inicial'],
    '结束地址': ['End address', '終了アドレス', 'Dirección final'],
    '注册国家代码': ['Registration country code', '登録国コード', 'Código de país del registro'],
    '地址版本': ['IP version', 'IP バージョン', 'Versión de IP'],
    '查询状态': ['Query status', '検索状態', 'Estado de consulta'],
    '已完成': ['Complete', '完了', 'Completado'],
    '部分来源不可用': ['Some sources unavailable', '一部の情報源は利用できません', 'Algunas fuentes no están disponibles'],
    '失败记录类型': ['Failed record types', '失敗したレコード種別', 'Tipos de registro fallidos'],
    '截断记录类型': ['Truncated record types', '省略したレコード種別', 'Tipos de registro truncados'],
    '用户名': ['Username', 'ユーザー名', 'Usuario'],
    '显示名称': ['Display name', '表示名', 'Nombre visible'],
    '账号类型': ['Account type', 'アカウント種別', 'Tipo de cuenta'],
    '公开仓库数': ['Public repositories', '公開リポジトリ数', 'Repositorios públicos'],
    '粉丝数': ['Followers', 'フォロワー数', 'Seguidores'],
    '关注数': ['Following', 'フォロー数', 'Siguiendo'],
    '最近公开仓库': ['Recent public repositories', '最近の公開リポジトリ', 'Repositorios públicos recientes'],
    '连接地址': ['Connected address', '接続アドレス', 'Dirección conectada'],
    '响应类型': ['Content type', 'コンテンツ種別', 'Tipo de contenido'],
    '服务器标识': ['Server header', 'サーバーヘッダー', 'Cabecera de servidor'],
    '跳转链': ['Redirect chain', '転送履歴', 'Cadena de redirecciones'],
    '响应耗时 ms': ['Response time (ms)', '応答時間 (ms)', 'Tiempo de respuesta (ms)'],
    '证书颁发者': ['Certificate issuer', '証明書発行者', 'Emisor del certificado'],
    '证书生效时间': ['Certificate valid from', '証明書有効開始', 'Certificado válido desde'],
    '证书到期时间': ['Certificate expires', '証明書有効期限', 'Vencimiento del certificado'],
    '证书剩余天数': ['Certificate days remaining', '証明書残り日数', 'Días restantes del certificado'],
    '证书覆盖域名': ['Certificate DNS names', '証明書 DNS 名', 'Dominios del certificado'],
})
for kind, key in (('域名档案', 'domain'), ('DNS 记录', 'dns'), ('网站与证书', 'website'),
                  ('IP 注册网络', 'network'), ('GitHub 公开资料', 'github')):
    FIELDS[kind] = [UI[lang][key] for lang in ('en', 'ja', 'es')]

for language, suffix in {
    'zh': '\n\n公开资源模块：域名档案查注册商/日期/NS；DNS 查8种记录；网站与证书查公网 HTTPS 响应、跳转、证书和响应头；IP/ASN 查注册网段；GitHub 查公开简介、计数和最近仓库。来源链接可以打开核实。第三方限流会标注部分来源不可用。',
    'en': '\n\nPublic resources: domain registration, 8 DNS record types, public HTTPS response/redirects/TLS/headers, IP/ASN registry and GitHub public profiles/repositories. Open source URLs to verify. Rate limits are shown as partial availability.',
    'ja': '\n\n公開情報：ドメイン登録、8種のDNS、公開HTTPS応答・転送・TLS・ヘッダー、IP/ASN登録情報、GitHub公開プロフィールとリポジトリ。情報源URLで確認できます。利用制限は一部取得不可として表示します。',
    'es': '\n\nRecursos públicos: registro de dominio, 8 tipos DNS, respuesta HTTPS/redirecciones/TLS/cabeceras, registro IP/ASN y perfiles/repositorios públicos de GitHub. Abre la fuente para verificar. Los límites se muestran como disponibilidad parcial.'
}.items():
    UI[language]['help_body'] += suffix

for language, value in {
 'zh':'部分公开来源未返回完整结果，可打开来源核实',
 'en':'Some public data is unavailable; open the source to verify',
 'ja':'一部の公開情報が取得できません。情報源で確認してください',
 'es':'Faltan algunos datos públicos; abre la fuente para comprobar'
}.items():
 UI[language]['limited']=value
