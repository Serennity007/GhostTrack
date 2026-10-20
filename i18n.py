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

def localize(value, lang):
    if isinstance(value, bool):
        return {'zh': ('否','是'), 'en': ('No','Yes'), 'ja': ('いいえ','はい'), 'es': ('No','Sí')}[lang][value]
    if value is None:
        return '—'
    if lang == 'zh' or value not in FIELDS:
        return value
    return FIELDS[value][{'en':0,'ja':1,'es':2}[lang]]
