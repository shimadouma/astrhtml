# Claude Code プロジェクト設定

このプロジェクトのClaude Code固有の設定と情報をまとめています。

## プロジェクト概要

**アークナイツ ストーリーアーカイブ**

アークナイツのイベントストーリーをHTML形式で閲覧できる静的サイトジェネレーターです。ArknightsStoryJsonのデータを使用してストーリーを処理・生成し、GitHub Pagesで公開します。

## 主要機能

- **自動ストーリー順序決定**: stage_table.jsonを参照してゲーム内と同じ順序でストーリーを表示
- **戦闘情報表示**: 戦闘前・戦闘後・間章の区別と推奨レベル表示
- **レスポンシブデザイン**: モバイル・デスクトップ両対応
- **自動デプロイ**: GitHub Actionsによる毎日の自動更新

## ビルドコマンド

```bash
# 全イベントのビルド
python3 build.py

# テスト用（少数イベント）
python3 build.py --limit 5

# クリーンビルド
python3 build.py --clean

# 依存関係のインストール
pip install -r requirements.txt
```

## テストコマンド

```bash
# 依存関係が正しくインストールされているかチェック
python3 -c "import jinja2, pathlib; print('Dependencies OK')"

# ビルドシステムの動作確認
python3 build.py --limit 1

# サブモジュールの更新
git submodule update --remote --merge
```

## 重要なファイル

### データ処理
- `src/lib/stage_parser.py` - ステージ情報とストーリー順序決定
- `src/lib/event_parser.py` - イベント情報の処理
- `src/lib/story_parser.py` - ストーリーデータの解析

### HTML生成
- `src/generators/` - HTML生成モジュール群
- `templates/` - Jinja2テンプレート
- `static/css/` - スタイルシート

### 設定・ビルド
- `build.py` - メインビルドスクリプト
- `src/config.py` - 設定ファイル
- `.github/workflows/deploy.yml` - GitHub Actions設定

## 開発時の注意事項

1. **サブモジュール**: ArknightsStoryJsonデータは外部サブモジュールです
   ```bash
   git submodule update --init --recursive
   ```

2. **Python要件**: Python 3.8以上を使用してください

3. **ビルド前の確認**: 
   - `data/ArknightsStoryJson`ディレクトリが存在することを確認
   - requirements.txtの依存関係をインストール済みであることを確認

4. **HTMLファイル名**: 
   - イベントページ: `events/{event_id}/index.html`
   - ストーリーページ: `events/{event_id}/stories/{stage_code}.html`
   - ステージコード（OR-1、OR-ST-1等）がファイル名として使用されます

## トラブルシューティング

### よくある問題と解決法

1. **ImportError**: 
   ```bash
   pip install -r requirements.txt
   ```

2. **サブモジュールが空**:
   ```bash
   git submodule update --init --recursive
   ```

3. **ビルドエラー**:
   - Python 3.8以上を使用していることを確認
   - `data/ArknightsStoryJson`が存在することを確認

## デプロイメント

- **自動デプロイ**: mainブランチへのプッシュで自動実行
- **手動デプロイ**: `./scripts/deploy.sh`を実行
- **GitHub Pages**: Actions経由で自動設定

## ライセンスと免責事項

- 非公式のファンプロジェクトです
- ストーリーデータはArknightsStoryJsonプロジェクトを使用
- アークナイツの著作権はHypergryphに帰属