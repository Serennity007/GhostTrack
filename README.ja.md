# GhostTrack Console

[简体中文](README.md) · [English](README.en.md) · **日本語** · [Español](README.es.md) · [Français](README.fr.md)

**Windows と Android で使える、公開情報調査のための OSINT ワークベンチ。**

ドメイン登録情報、DNS、TLS 証明書、IP / ASN の登録情報、公開プロフィールを一つのコンソールに集約。Windows の 12 ツールと Android の 11 モジュールが共通の検索エンジンを使い、取得した結果を絞り込み・コピー・エクスポートまで一貫して扱えます。

- **一度の検索でドメインを把握。** RDAP、8 種類の DNS レコード、HTTPS / TLS 情報を並列取得し、取得元ごとの状態を表示します。
- **情報源と検索時点を結果に残す。** 取得できた情報源の URL と UTC の検索日時を確認し、項目の絞り込み、値のコピー、JSON・CSV・単独で閲覧できる HTML レポートへの出力ができます。
- **デスクトップでもスマートフォンでも。** Windows の左右 2 列のワークスペースと Android のネイティブ画面を用意。画面は 4 言語に対応し、配布パッケージは Python を別途インストールせずに使えます。

> ドキュメントは中国語・英語・日本語・スペイン語・フランス語の 5 言語です。アプリの画面は簡体字中国語・英語・日本語・スペイン語の 4 言語に対応しています。

## ダウンロードとインストール

| 対応環境 | 最新版のダウンロード | インストール |
|---|---|---|
| Windows 10/11 x64 · v1.8.0 | [ポータブル ZIP](https://github.com/Serennity007/GhostTrack/releases/download/windows-v1.8.0/GhostTrack-v1.8.0-Windows-x64.zip) · [リリース・SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/windows-v1.8.0) | 全体を展開し、`GhostTrack/GhostTrack.exe` を実行 |
| Android 7.0 以降 · v1.6.0 | [ユニバーサル APK](https://github.com/Serennity007/GhostTrack/releases/download/android-v1.6.0/GhostTrack-v1.6.0-Android-universal.apk) · [リリース・SHA256](https://github.com/Serennity007/GhostTrack/releases/tag/android-v1.6.0) | スマートフォンのファイル管理アプリで APK を開く |

Windows 版に Python のインストールは不要です。EXE だけを移動せず、付属ファイルを同じフォルダーに残してください。Android 版は ARM64・ARMv7・x86_64 を含み、初回起動時に内蔵ランタイムを展開します。APK を開くアプリにのみインストールを許可してください。更新には本リポジトリの同じ証明書で署名された APK を使用します。

[Windows ガイド（中国語）](README_WINDOWS.md) · [Android の使用・ビルド（中国語）](README_ANDROID.md) · [変更履歴](CHANGELOG.md)

## 画面

![Windows 公開情報コンソール](docs/desktop.png)

<img src="docs/android.png" width="320" alt="Android 公開情報コンソール" />

Windows v1.8.0 は左右 2 列のワークスペースを採用しています。

- 左側に入力・サンプル・取得元の説明、右側に結果一覧と値の全文表示を配置。
- コンパクトな番号付きナビゲーションに 12 ツールを集約し、実際の項目数・経過時間・検索状態をカードに表示。
- ウィンドウ幅に合わせて操作バーが調整され、絞り込み・コピー・出力を結果の近くで操作可能。

装飾の図形は対象へのスキャン実行を示しません。結果と状態は実際に取得したデータに基づきます。Android の最新版は引き続き v1.6.0 です。

## 12 種類の検索ツール

| ツール | 入力 | 取得できる公開情報 |
|---|---|---|
| 認定アーカイブ | 電話番号またはキーワード | この端末に保存した認可済みの番号・プロフィール関連付け、情報源、保存日時 |
| ドメイン総合レポート | ドメイン | RDAP・DNS・HTTPS を並列取得し、取得元ごとの状態を表示 |
| ドメイン登録情報 | ドメイン | レジストラ、登録・有効期限・更新日、DNSSEC、ネームサーバー |
| DNS レコード | ドメイン | A・AAAA・CNAME・MX・NS・TXT・SOA・CAA と TTL |
| Web サイトと証明書 | 公開 HTTPS URL | HTTP 状態、タイトル、リダイレクト、公開ヘッダー、TLS 発行者・有効期間・SAN |
| IP / ASN 登録情報 | 公開 IP または `AS15169` | 登録範囲、CIDR、ネットワーク名、国コード、日付 |
| GitHub 公開プロフィール | ユーザー名またはプロフィール URL | 公開自己紹介、各種件数、作成日、直近 5 件の公開リポジトリ |
| 中国の公開プロフィール | プロフィール URL・共有文・プラットフォームのユーザー ID | 取得可能なタイトル、説明、アクセス状態、取得元、検索時刻 |
| IP の地域情報 | 公開 IPv4 / IPv6 | データベース上の推定地域、組織、プロバイダー、ASN、タイムゾーン |
| 自分の公開 IP | 入力不要 | 現在のネットワークの外向き公開 IP |
| 電話番号メタデータ | 電話番号と既定の地域 | ローカル解析による番号帯の地域、通信事業者、タイムゾーン、形式、妥当性 |
| ユーザー名リンク | ユーザー名 | GitHub・Instagram・X のリンクを生成。アカウントの存在は未確認 |

対応プラットフォームは **抖音（Douyin）、小紅書（Xiaohongshu）、快手、Bilibili、微博、知乎、豆瓣** です。完全なプロフィール URL の貼り付けを推奨します。抖音・小紅書の一部プロフィール共有短縮リンクにも対応します。表示名、抖音のハンドル、動画・投稿のリンクは、必要なプロフィール ID の代わりにはなりません。

## 結果の操作

- 入力例の挿入だけでは通信しません。検索を中止すると、遅れて届いた応答は表示・保存されません。
- 項目名・内容で絞り込み、全文確認、単一値・全結果のコピー、取得元の確認ができます。
- ツール名・入力・UTC 時刻付きの JSON、UTF-8 BOM CSV、単体 HTML を出力します。CSV では数式として扱われる文字列を保護します。
- Windows はダブルクリック / Ctrl+C でコピー、Enter で検索、Esc で中止。Android はタッチ操作とシステムのファイル選択画面で出力します。
- Windows のセッション履歴は最大 50 件です。再起動後の保存は任意で、既定では無効です。Android は検索履歴を永続保存せず、言語と選択ツールだけを記憶します。
- 「アーカイブに保存」で、プラットフォーム結果のプロフィールと、本人許可または公開された電話番号の関連付けを情報源・保存日時とともに記録。サイドバーのアーカイブ管理で削除・エクスポート、モジュール 12 で番号・キーワード検索ができます。

## 取得元・プライバシー・制限

[RDAP](https://about.rdap.org/)、[Google Public DNS](https://developers.google.com/speed/public-dns/docs/doh/json)、[GitHub 公開 API](https://docs.github.com/en/rest/users/users#get-a-user)、ipwho.is、api.ipify.org、および入力された公開 Web サイト・プロフィールを利用します。ネットワーク検索の対象は対応する取得元へ送られます。電話番号メタデータはローカルで解析します。プロジェクトの中継サーバー、アカウントログイン、利用状況の送信はありません。

ログイン、CAPTCHA、JavaScript、レート制限、障害により結果が制限される場合があります。取得できた情報と状態を保持し、アクセス制御を回避しません。HTTP 200 だけでは本人確認済みと判断しません。Web サイト検索は公開 HTTPS のポート 443 のみを対象に、証明書を検証し、転送回数と応答サイズを制限します。欠落値を推測で埋めず、RDAP の登録者連絡先も出力しません。

**電話番号帯の地域や IP データベースの位置は、端末の現在地ではありません。電話番号から非公開アカウントを特定する機能、実名の特定、プラットフォーム間の本人照合はありません。認定アーカイブは情報源を明示して自分で保存した関連付けのみをこの端末に保持し、いつでも削除できます。** アクセス権のある公開情報のみを調べ、各サービスの利用条件を守ってください。

Windows の設定と任意の履歴は `%LOCALAPPDATA%\GhostTrackDesk` に保存され、アプリから履歴を消去できます。エラーログに検索内容は記録しません。Android が要求するのはインターネット権限のみで、位置情報・連絡先・SMS・電話・ストレージ全体の権限は不要です。出力ファイル、クリップボード、共有 URL に検索内容が含まれる場合があるため、適切に管理してください。

## 開発とビルド

Python 3.11 x64 を使用します。Windows の例：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe desktop.py
.\.venv\Scripts\python.exe build_windows.py
```

Android は JDK 17 と Android SDK Platform 36 / Build Tools 36.0.0 が必要です。Gradle Wrapper を同梱しています。

```powershell
$env:JAVA_HOME = 'JDK 17 のパス'
$env:ANDROID_HOME = 'Android SDK のパス'
.\.venv\Scripts\python.exe build_android.py --gradle .\android\gradlew.bat
```

ビルドスクリプトはテストを実行し、配布ファイルと SHA256 を生成します。Android では Lint と署名検証も実行します。署名鍵は Git に入れず、[Android ガイド](README_ANDROID.md)に従って安全にバックアップしてください。[Windows ワークフロー例](docs/windows-workflow.example.yml)はテンプレートであり、ホスト型 CI の稼働を示すものではありません。

## 原作者と不具合報告

[HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) を拡張し、元の `GhostTR.py` と[元プロジェクトの説明](UPSTREAM_README.md)を残しています。各プラットフォームの公式クライアントではありません。

[Issues](https://github.com/Serennity007/GhostTrack/issues) には OS、アプリのバージョン、再現手順を記載してください。トークン、秘密鍵、個人の検索履歴、非公開リンクは添付しないでください。
