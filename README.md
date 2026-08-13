# i-bloom-stock-bot

i-BLOOM SQUISHY SHOP (https://i-bloom.shop/collections/all-items) の
「在庫あり」「在庫切れ」件数を60分ごとに監視し、Discordに通知するbotです。
毎回の件数は `data/stock_history.csv` に蓄積されるので、後でグラフ化などに使えます。

## 仕組み

- 商品一覧ページのHTMLを取得し、絞り込みフィルターに表示されている
  `在庫あり (32個の商品)` / `在庫切れ (331個の商品)` の数字をそのまま抜き出します。
  (サイト上で見えているフィルター件数と同じ値になります)
- 取得した数字を Discord Webhook 宛に通知します。
- 同時に `data/stock_history.csv` に1行追記します。
- GitHub Actions の `schedule`(cron) で1時間ごとに自動実行し、
  実行後に更新されたCSVを自動でコミット・プッシュします。

## セットアップ手順

### 1. Discord Webhook URLを発行する

Discordサーバーの通知したいチャンネル → 設定 →連携サービス → ウェブフック →
「新しいウェブフック」を作成し、Webhook URLをコピーしておく。

### 2. GitHubリポジトリを作る

このフォルダの中身をそのまま新しいGitHubリポジトリにpushしてください。

```bash
cd ibloom-stock-bot
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<あなたのアカウント>/<リポジトリ名>.git
git push -u origin main
```

### 3. Secretsを設定する

GitHubリポジトリの Settings → Secrets and variables → Actions → New repository secret

- Name: `DISCORD_WEBHOOK_URL`
- Value: 手順1でコピーしたWebhook URL

### 4. Actionsの権限を確認する

Settings → Actions → General → Workflow permissions で
「Read and write permissions」になっていることを確認してください
(CSVを自動コミットするために必要です)。

### 5. 動作確認

Actionsタブ → 「Stock Check」ワークフロー → 「Run workflow」で手動実行して、
Discordに通知が来ること、`data/stock_history.csv` が更新されることを確認してください。

以降は `cron: "0 * * * *"` の設定により、毎時0分ごろに自動実行されます。

## 注意点

- GitHub Actionsの`schedule`は指定時刻ちょうどではなく、
  サーバー負荷により数分〜十数分程度遅れることがあります(完全に正確な60分間隔ではありません)。
- publicリポジトリの場合、`data/stock_history.csv` は誰でも見られる状態になります。
  非公開にしたい場合はprivateリポジトリにしてください
  (privateでもGitHub Actionsの無料枠は使えます)。
- 60日間リポジトリへのコミットが無いと、GitHubの仕様でスケジュール実行が自動停止することがあります。
  その場合はActionsタブから手動で再度有効化(Run workflow)してください。
- サイト側のHTML構造(絞り込みフィルターの表記)が変わると、正規表現が
  マッチしなくなりエラーになります。その際は `check_stock.py` 内の
  `IN_STOCK_PATTERN` / `OUT_OF_STOCK_PATTERN` を現在のHTMLに合わせて調整してください。

## グラフを作りたくなったら

`data/stock_history.csv` はそのままExcel/Googleスプレッドシート/Pythonなどで
読み込んでグラフ化できます。お試し用に簡単なスクリプトも同梱しています。

```bash
pip install matplotlib pandas
python scripts/plot_history.py
```

`data/stock_history.png` に折れ線グラフが出力されます。
