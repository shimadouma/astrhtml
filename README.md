# アークナイツ ストーリーアーカイブ

アークナイツのイベントストーリーをHTML形式で閲覧できる静的サイトジェネレーターです。

## 概要

このプロジェクトは、アークナイツのゲーム内イベントストーリーを読みやすいHTML形式に変換し、GitHub Pagesで公開するためのツールです。[ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson)のデータを使用してストーリーを処理・生成します。

## 特徴

- **自動更新**: GitHub Actionsにより毎日最新のストーリーデータを取得・更新
- **読みやすい表示**: 会話形式のストーリーを整理されたレイアウトで表示
- **モバイル対応**: レスポンシブデザインでスマートフォンでも快適に閲覧可能
- **イベント分類**: イベントタイプ別の分類表示
- **ナビゲーション**: ストーリー間の前後移動、パンくずナビゲーション

## セットアップ

### 必要な環境

- Python 3.8以上
- Git

### インストール手順

1. リポジトリをクローン:
   ```bash
   git clone --recurse-submodules https://github.com/[username]/astrhtml.git
   cd astrhtml
   ```

2. Python依存関係をインストール:
   ```bash
   pip install -r requirements.txt
   ```

3. サブモジュールの更新:
   ```bash
   git submodule update --remote --merge
   ```

## 使用方法

### ローカルでのビルド

全てのイベントをビルド:
```bash
python build.py
```

テスト用に少数のイベントのみビルド:
```bash
python build.py --limit 5
```

特定のイベントのみビルド:
```bash
python build.py --event act15side
```

### GitHub Pagesでの公開

1. GitHubリポジトリにプッシュ
2. GitHub リポジトリの Settings > Pages で「GitHub Actions」を選択
3. `main`ブランチにプッシュすると自動的にデプロイが実行されます

### 手動デプロイ

```bash
./scripts/deploy.sh
```

## プロジェクト構造

```
astrhtml/
├── src/                    # Pythonソースコード
│   ├── models/            # データモデル
│   ├── lib/               # データ処理ライブラリ
│   ├── generators/        # HTML生成器
│   ├── utils/             # ユーティリティ関数
│   └── config.py          # 設定ファイル
├── templates/             # HTMLテンプレート
│   ├── base.html         # ベーステンプレート
│   ├── index.html        # インデックスページ
│   ├── event.html        # イベントページ
│   └── story.html        # ストーリーページ
├── static/               # 静的ファイル
│   └── css/              # スタイルシート
├── data/                 # データディレクトリ
│   └── ArknightsStoryJson/ # ストーリーデータ（サブモジュール）
├── dist/                 # ビルド出力先
├── build.py              # メインビルドスクリプト
└── requirements.txt      # Python依存関係
```

## 設定

`src/config.py`で以下の設定を変更できます：

- `MAX_EVENTS_PER_PAGE`: ページあたりの最大イベント数
- `INCLUDE_REPLICATE_EVENTS`: 復刻イベントを含めるかどうか
- `SORT_EVENTS_BY_DATE`: 日付順にソートするかどうか

## 開発

### 新機能の追加

1. `src/models/`にデータモデルを追加
2. `src/lib/`にデータ処理ロジックを追加
3. `templates/`にHTMLテンプレートを追加
4. `src/generators/`にHTML生成器を追加

### テスト

限定的なビルドでテスト:
```bash
python build.py --limit 1
```

## トラブルシューティング

### よくある問題

1. **サブモジュールが空の場合**:
   ```bash
   git submodule update --init --recursive
   ```

2. **Python依存関係のエラー**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **ビルドエラー**:
   - `data/ArknightsStoryJson`ディレクトリが存在することを確認
   - Python 3.8以上を使用していることを確認

## ライセンスと免責事項

- このプロジェクトは非公式のファンプロジェクトです
- ストーリーデータは[ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson)プロジェクトから取得しています
- アークナイツの著作権は上海鷹角網絡科技有限公司（Hypergryph）に帰属します
- このプロジェクトのコードはMITライセンスの下で公開されています

## 貢献

バグ報告や機能追加の提案は、GitHubのIssuesでお願いします。

## 関連リンク

- [アークナイツ公式サイト](https://www.arknights.jp/)
- [ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson)
- [GitHub Pages ドキュメント](https://docs.github.com/pages)