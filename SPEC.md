# プロジェクト別顧客満足度ダッシュボード 仕様書

> 作成日：2026-03-18
> 対象読者：このダッシュボードを新規構築・移植・カスタマイズしたい開発者

---

## 1. 概要

複数のGoogle Spreadsheetsに蓄積された顧客満足度アンケートデータを一元可視化するWebダッシュボード。
ログイン認証付き・リアルタイム更新・複数プロジェクト比較に対応。

### 主な機能

| 機能 | 内容 |
|---|---|
| ログイン認証 | ユーザー名/パスワードによるアクセス制限 |
| データ取得 | Google Sheets API（5分ごと自動更新） |
| プロジェクト比較 | 複数PJをカラー分けして同一グラフに重ね表示 |
| 期間フィルター | 年月単位でのデータ絞り込み |
| KPIカード | 平均・中央値・回答者数・NPS等を一覧表示 |
| カテゴリ別スコア | 動画・サポート・システムのゲージカード表示 |
| トレンドグラフ | 月別推移の折れ線グラフ（プロジェクト別色分け） |
| フリーコメント | 満足度スコア付きコメント一覧（10件ずつ表示） |
| デモモード | 実データなしでも動作確認できるサンプルデータ表示 |

---

## 2. 技術スタック

| 役割 | 技術 | バージョン |
|---|---|---|
| Webアプリ | Streamlit | >=1.55.0 |
| 認証 | streamlit-authenticator | >=0.4.2 |
| データ取得 | gspread + google-auth | >=6.2.1 / >=2.28.0 |
| データ処理 | pandas | >=2.3.3 |
| グラフ | plotly | >=6.6.0 |
| パスワードハッシュ | bcrypt | >=5.0.0 |
| 設定ファイル | PyYAML | >=6.0.3 |
| パッケージ管理 | uv（推奨）または pip | — |
| ホスティング | Streamlit Cloud（無料枠） | — |
| データソース | Google Sheets | — |

---

## 3. ファイル構成

```
satisfaction-dashboard/
├── app.py                  # メインアプリ・UI・ページ構成
├── auth.py                 # ログイン認証ロジック
├── data.py                 # Google Sheets取得・列名正規化・デモデータ生成
├── charts.py               # Plotlyグラフ生成（全チャート定義）
├── config.yaml             # ログインユーザー設定（Gitに含める）
├── generate_password_hash.py  # パスワードハッシュ生成ユーティリティ
├── requirements.txt        # 依存パッケージ一覧
├── pyproject.toml          # プロジェクト設定
└── .streamlit/
    ├── config.toml         # Streamlitテーマ設定（Gitに含める）
    └── secrets.toml        # APIキー・認証情報（Gitに含めない）
```

---

## 4. セットアップ手順

### 4-1. リポジトリのクローンと環境構築

```bash
git clone https://github.com/<your-org>/satisfaction-dashboard.git
cd satisfaction-dashboard

# uv を使う場合
uv sync

# pip を使う場合
pip install -r requirements.txt
```

### 4-2. Google Cloud 設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→「有効なAPI」から以下を有効化
   - Google Sheets API
   - Google Drive API
3. 「認証情報」→「サービスアカウント」を作成し、JSONキーをダウンロード
4. データを読み込みたい各Spreadsheetを、サービスアカウントのメールアドレスと **「閲覧者」** で共有

### 4-3. secrets.toml の作成

`.streamlit/secrets.toml` を以下の形式で作成（Gitには含めない）：

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "xxxx"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "xxxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

[sheets]
# 読み込む Spreadsheet の ID を列挙（URLの /d/〇〇/ の部分）
spreadsheet_ids = [
  "1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "1yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
]

[app]
# ログイン画面をスキップ（開発・テスト時のみ true に）
dev_mode = false
# "demo" にするとサンプルデータで動作（実データなしで確認したいとき）
data_mode = ""
```

### 4-4. ログインユーザーの設定

`config.yaml` を編集してユーザーを追加する：

```bash
# パスワードハッシュの生成
python generate_password_hash.py
```

`config.yaml` の構造：

```yaml
credentials:
  usernames:
    your_username:
      email: your@email.com
      name: 表示名
      password: "$2b$12$..."   # bcryptハッシュ

cookie:
  expiry_days: 7
  key: "ランダムな秘密鍵文字列"  # 必ず変更すること
  name: "satisfaction_dashboard_cookie"
```

### 4-5. ローカル起動

```bash
# 通常起動（ポート8501）
streamlit run app.py

# 別ポートで起動（他のローカル開発と被る場合）
streamlit run app.py --server.port 8502
```

---

## 5. Streamlit Cloud へのデプロイ

1. GitHubにリポジトリをpush（`secrets.toml` は `.gitignore` で除外済み）
2. [share.streamlit.io](https://share.streamlit.io) でアカウント作成
3. 「New app」→ リポジトリ・ブランチ・`app.py` を指定
4. 「Advanced settings」→「Secrets」に `secrets.toml` の内容を貼り付け
5. Deploy

> ⚠️ 無料枠ではリポジトリを **Public** にする必要あり

---

## 6. データ形式の要件

### 6-1. Spreadsheet の構造

- タブ名に **「満足度」** を含むシートのみ自動で読み込まれる
- ヘッダー行は1行目でなくてもOK（キーワードで自動検出）
- 以下の列名を使うと自動マッピングされる

### 6-2. 列名マッピング（認識される列名一覧）

| 正規化後の名前 | 認識される列名の例 |
|---|---|
| `date`（日付） | `回答日時` `日付` `回答日` `date` |
| `project_name`（PJ名） | `プロジェクト名` `project_name`（なければタブ名を使用） |
| `video_score`（動画満足度 /10） | `動画カリキュラムの満足度はいかがですか？（10段階）` `コンテンツ` |
| `support_score`（サポート満足度 /10） | `サポートの満足度はいかがですか？（10段階）` `サポート` |
| `system_score`（システム満足度 /10） | `システムの使いやすさはいかがですか？（10段階）` `システム` |
| `self_effort_score`（取り組み /100） | `ここまでの学習を振り返ってみて…（100点満点中）` `自身取組み` |
| `nps_score`（おすすめ度 /10） | `あなたは当校をどの程度友人や知人に勧めますか？` `おすすめ度` `NPS` |
| `comment`（自由記述） | `動画カリキュラムについて、改善点や…` `コメント` `感想` |
| `total_students`（受講生数） | `受講生数` |
| `respondents`（回答者数） | `回答者数` |

> 上記にない列名でも、キーワードが含まれていれば自動推定される。
> 例：`取り組みスコア（100点）` → `self_effort_score` として認識

### 6-3. score（総合満足度）の計算

- `score` 列が存在する場合はそのまま使用
- なければ `video_score`・`support_score`・`system_score` の平均を自動計算

---

## 7. 新しいシート・プロジェクトの追加方法

### 同じフォーマットで別プロジェクトを追加（コード変更なし）

1. Spreadsheet のタブ名に「満足度」を含める（例：`満足度：新PJ`）
2. ヘッダー行に上記の列名を使う
3. サービスアカウントと共有
4. `secrets.toml` の `spreadsheet_ids` にIDを追記
5. Streamlit Cloud の Secrets を更新

### プロジェクト名の上書き（タブ名を変えたくない場合）

`secrets.toml` に以下を追記：

```toml
[sheet_project_overrides]
"Spreadsheet_ID" = "表示したいプロジェクト名"
```

---

## 8. 動作モード

| モード | 設定方法 | 動作 |
|---|---|---|
| 通常モード | デフォルト | ログイン必須、実データ表示 |
| デモモード | `data_mode = "demo"` | ログイン必須、サンプルデータ表示 |
| 開発モード | `dev_mode = true` | ログインスキップ |
| 開発+デモ | 両方設定 | ログインスキップ + サンプルデータ |

---

## 9. カスタマイズポイント

### テーマカラーの変更（`.streamlit/config.toml`）

```toml
[theme]
primaryColor = "#4F46E5"      # メインカラー（ボタン・アクセント）
backgroundColor = "#F8FAFC"   # 背景色
```

### プロジェクトカラーパレット（`app.py`）

```python
_PROJECT_COLORS = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#F43F5E", "#8B5CF6"]
```

プロジェクト数が6を超えると最初の色に戻る（ループ）。

### 目標ラインの変更（`charts.py`）

```python
fig.add_hline(y=8, ...)   # 満足度の目標値（デフォルト: 8.0 / 10）
fig.add_hline(y=70, ...)  # 取り組みの目標値（デフォルト: 70 / 100）
```

### データキャッシュの更新間隔（`data.py`）

```python
@st.cache_data(ttl=300)  # 300秒 = 5分ごとに再取得
```

---

## 10. トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 「データが取得できませんでした」 | サービスアカウントへの共有忘れ | Spreadsheetを閲覧者として共有 |
| データは表示されるが全部0や— | 列名がマッピングされていない | 6-2の列名一覧と照合 |
| ログインできない | config.yaml のパスワードが違う | `generate_password_hash.py` で再生成 |
| Streamlit Cloudでエラー | Secrets が古い | Secrets を最新の secrets.toml で更新 |
| グラフが空 | 日付列が認識されていない | 列名を `回答日時` に変更 |
| デプロイできない（Private repo） | 無料枠の制限 | リポジトリを Public に変更 |

---

## 11. セキュリティ注意事項

- `secrets.toml` は絶対にGitにコミットしない（`.gitignore` で除外済み）
- `config.yaml` のパスワードはbcryptハッシュ化済みのもののみ保存
- `cookie.key` は本番環境では必ずランダムな文字列に変更する
- サービスアカウントの権限は「閲覧者のみ」に限定する（書き込み不要）
- リポジトリを Public にする場合、機密情報が `config.yaml` に含まれないよう注意

---

## 12. 依存関係

```
streamlit>=1.55.0
gspread>=6.2.1
google-auth>=2.28.0
streamlit-authenticator>=0.4.2
pandas>=2.3.3
plotly>=6.6.0
bcrypt>=5.0.0
PyYAML>=6.0.3
toml>=0.10.2
```
