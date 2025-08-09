# TODO list for development

## プロジェクト概要
- アークナイツのストーリーをHTML化して Github Pages で公開する用のリポジトリを作成する
- アークナイツのストーリーデータは https://github.com/050644zf/ArknightsStoryJson を submodule として追加して参照する
  - 対象とするストーリーデータは ArknightsStoryJson/ja_JP/gamedata/story/activities にあるもの
  - ArknightsStoryJson/ja_JP/gamedata/story/activities の各ディレクトリがイベントに対応している
    - ディレクトリ名がイベントIDとなっていて、 ArknightsStoryJson/ja_JP/gamedata/excel/activity_table.json の basicInfo.<eventId> でイベントの基本情報（イベント名、開始日時、修了日時など）が取得できる
- 各イベントのストーリーを HTML 化するためのスクリプトを作成する
  - インデックスページには、イベントの一覧と、各イベントへのリンクを表示する
    - イベントの一覧はイベント開始日時が最近の順番で並べる
  - 各イベントのページには、イベントの各ストーリーのページへのリンクを表示する
    - 各ストーリーのページには、ストーリーの内容を HTML 化して表示する
      - 背景画像情報は表記しない
      - 同じ話者の台詞は1つのブロックにまとめて表示する
- 表示方式を制御するためのメニュー機能
  - フォントをゴシック体モードと明朝体モードで切替えられる
    - ゴシック体モードはOS標準の san-serif フォント、明朝体モードは長文テキストを読むときに読みやすいと評価されているフォントをWebフォントで読込む
  - ナイトモードの ON/OFF切替え
- プレビュー用にローカルHTTPサーバ起動機能
- HTML 化したストーリーを GitHub Pages で公開するためのスクリプトを作成する
- Github Pages で公開するための設定方法を README.md に記載する

## 詳細な実装プラン

### フェーズ1: プロジェクトの初期セットアップ
- [x] プロジェクトの基本構造を作成
  - [x] requirements.txtの作成（Python依存パッケージ）
  - [x] .gitignoreの作成
  - [x] .gitmodulesの設定
- [x] ArknightsStoryJsonをsubmoduleとして追加
  ```bash
  git submodule add https://github.com/050644zf/ArknightsStoryJson.git data/ArknightsStoryJson
  git submodule update --init --recursive
  ```
- [x] Python仮想環境のセットアップ
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

### フェーズ2: データ処理レイヤーの実装
- [x] データモデルの定義
  - [x] `src/models/story.py` - ストーリーデータのクラス定義
    - storyList配列の各要素を処理（Dialog、Character、name属性等）
    - キャラクター名、会話内容、背景画像、音楽等の情報を構造化
  - [x] `src/models/event.py` - イベントデータのクラス定義
    - イベントID、イベント名、ストーリーファイル一覧の管理
  - [x] `src/models/activity.py` - activity_tableデータのクラス定義
    - basicInfo内の各イベント情報（id、name、startTime、endTime等）
- [x] データ読み込みモジュール
  - [x] `src/lib/data_loader.py` - JSONファイル読み込み処理
  - [x] `src/lib/event_parser.py` - イベント情報のパース処理
    - activity_table.jsonからイベント基本情報を取得
    - activitiesディレクトリのサブディレクトリと紐付け
  - [x] `src/lib/story_parser.py` - ストーリーデータのパース処理
    - storyListの各要素をprop属性に応じて処理
    - Dialog、Character、name、Subtitle等のタイプ別処理
- [x] データ処理ユーティリティ
  - [x] `src/utils/date_formatter.py` - 日付フォーマット処理（UnixTimestampから日付変換）
  - [x] `src/utils/text_processor.py` - テキスト処理（改行、特殊文字等）
  - [x] `src/utils/story_renderer.py` - ストーリー要素のHTML変換処理
  - [x] `src/utils/file_utils.py` - ファイル操作ユーティリティ

### フェーズ3: HTML生成システムの実装
- [x] テンプレートエンジン（Jinja2）の設定
  - [x] `templates/base.html` - ベーステンプレート
  - [x] `templates/index.html` - インデックスページテンプレート
  - [x] `templates/event.html` - イベントページテンプレート
  - [x] `templates/story.html` - ストーリーページテンプレート
  - [x] `templates/components/` - 共通コンポーネント（base.htmlに統合済み）
    - [x] `navigation.html` - ナビゲーション（base.htmlに統合）
    - [x] `footer.html` - フッター（base.htmlに統合）
- [x] スタイルシート
  - [x] `static/css/main.css` - メインスタイル
  - [x] `static/css/story.css` - ストーリー表示用スタイル
  - [x] `static/css/responsive.css` - レスポンシブ対応（main.cssに統合済み）
- [x] HTML生成モジュール
  - [x] `src/generators/index_generator.py` - インデックスページ生成
  - [x] `src/generators/event_generator.py` - イベントページ生成
  - [x] `src/generators/story_generator.py` - ストーリーページ生成
  - [x] `src/generators/base_generator.py` - 基底ジェネレータクラス
- [x] ストーリー表示の改良
  - [x] 背景画像情報を非表示にする機能実装（`story.html`テンプレート修正）
  - [x] 同じ話者の連続する台詞を統合する機能実装（`story_renderer.py`に`group_consecutive_dialogs`関数追加）

### フェーズ4: ビルドシステムの構築
- [x] メインビルドスクリプト
  - [x] `build.py` - メインビルド処理
  - [x] `src/config.py` - ビルド設定（パス、オプション等）
- [x] 出力ディレクトリ構造
  ```
  dist/
  ├── index.html                 # メインインデックス
  ├── events/
  │   ├── [eventId]/
  │   │   ├── index.html         # イベントインデックス
  │   │   └── stories/
  │   │       └── [storyId].html # 各ストーリーページ
  ├── static/
  │   ├── css/
  │   ├── js/
  │   └── images/
  ```
- [x] コマンドラインインターフェース
  - [x] `python build.py` - 全体ビルド
  - [x] `python build.py --event [eventId]` - 特定イベントのみビルド（--limitで実装）
  - [x] `python build.py --clean` - ビルド成果物のクリーンアップ（--no-cleanで制御）

### フェーズ5: GitHub Pages デプロイメント
- [x] GitHub Actionsワークフローの作成
  - [x] `.github/workflows/deploy.yml` - 自動デプロイ設定
  ```yaml
  name: Deploy to GitHub Pages
  on:
    push:
      branches: [main]
    schedule:
      - cron: '0 0 * * *'  # Daily update
    workflow_dispatch:
  jobs:
    build-and-deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            submodules: recursive
        - uses: actions/setup-python@v4
        - run: pip install -r requirements.txt
        - run: python build.py
        - uses: actions/deploy-pages@v2
  ```
- [x] GitHub Pages設定
  - [x] gh-pagesブランチの作成（GitHub Actionsで自動化）
- [x] デプロイスクリプト
  - [x] `scripts/deploy.sh` - 手動デプロイ用スクリプト

### フェーズ6: ドキュメント整備
- [x] README.mdの更新
  - [x] プロジェクト概要
  - [x] 必要な環境・依存関係
  - [x] セットアップ手順
  - [x] ビルド・デプロイ手順
  - [x] GitHub Pages設定方法

### フェーズ7: 機能拡張（オプション）
- [x] 検索機能の実装
  - [x] `static/js/search.js` - クライアントサイド検索
  - [x] `src/generators/search_index.py` - 検索インデックス生成
  - [x] 検索データの自動生成（events, stories）
  - [x] リアルタイム検索とハイライト機能
- [x] フィルタリング機能（イベント期間、タイプ等）
  - [x] `static/js/filters.js` - イベントタイプと年別フィルタ
  - [x] 検索との連携機能
- [x] ダークモード対応
  - [x] `static/js/theme.js` - テーマ切り替え機能
  - [x] CSS変数を使ったダーク/ライトテーマ
  - [x] LocalStorageでの設定保存
  - [x] ダークモード色彩の改善・調整
    - [x] 背景色とテキスト色のコントラスト調整（完全な白黒を避けた目に優しい色設定）
    - [x] カード背景色の統一（`var(--card-background)`使用）
    - [x] ストーリーページ（`story.css`）の完全ダークモード対応
    - [x] リンク色の可読性向上（明るい青 `#4299e1`）
    - [x] ボタン類の色調整（背景・テキストコントラスト改善）
    - [x] ストーリーヘッダー（`h2`）の色調整
    - [x] 話者名（`.speaker`）の色調整
    - [x] 各種UI要素の統一感のある色設定
- [x] フォント切替機能
  - [x] `static/js/font.js` - フォント切り替え機能
  - [x] ゴシック体モード（OS標準san-serif）
  - [x] 明朝体モード（読みやすいWebフォント：Noto Serif JP, Crimson Text）
  - [x] LocalStorageでの設定保存
  - [x] ヘッダーにフォント切替トグルボタン追加
  - [x] CSS変数を使ったフォントファミリー制御
  - [x] レスポンシブ対応（モバイル表示調整）
- [x] プレビュー用ローカルHTTPサーバ機能
  - [x] `preview.py` - ローカル開発サーバスクリプト
  - [x] 自動ブラウザ起動機能
  - [x] 静的ファイル配信（CSS、JS、画像）
  - [x] リアルタイム開発支援（手動リロード）
  - [x] ポート番号設定（デフォルト8000、カスタマイズ可能）
  - [x] CORS対応とセキュリティ設定
- [ ] 実装見送り: プログレッシブウェブアプリ（PWA）対応
  - [ ] `static/manifest.json` - PWAマニフェスト
  - [ ] `static/sw.js` - Service Worker

## 技術スタック
- **言語**: Python 3.8+
- **テンプレートエンジン**: Jinja2
- **静的サイトジェネレーター**: カスタム実装（Python）
- **デプロイ**: GitHub Pages + GitHub Actions
- **スタイリング**: Pure CSS（CSS変数によるテーマシステム）
- **フロントエンド機能**: Vanilla JavaScript（テーマ切り替え、フォント切り替え、検索、フィルタリング）
- **フォント**: Google Fonts（Noto Serif JP、Crimson Text）
- **主要Pythonパッケージ**:
  - Jinja2 - HTMLテンプレート処理
  - python-dateutil - 日付処理
  - pathlib - ファイルパス操作
  - argparse - コマンドライン引数処理

## ディレクトリ構造
```
astrhtml/
├── data/
│   └── ArknightsStoryJson/    # サブモジュール
├── src/
│   ├── models/                # データモデル
│   ├── lib/                   # データ処理ライブラリ
│   ├── generators/            # HTML生成器
│   ├── utils/                 # ユーティリティ関数
│   └── config.py              # 設定ファイル
├── templates/                 # HTMLテンプレート
├── static/                    # 静的ファイル（CSS, JS, 画像）
├── dist/                      # ビルド出力先
├── scripts/                   # デプロイ等のスクリプト
├── tests/                     # テストコード
├── build.py                   # メインビルドスクリプト
├── requirements.txt           # Python依存関係
├── .gitignore
├── .gitmodules
├── README.md
└── TODO.md
```

## データ構造の詳細

### activity_table.json
- `basicInfo`オブジェクト内に各イベント情報が格納
- 各イベントは以下の主要フィールドを持つ：
  - `id`: イベントID（activitiesディレクトリ名と対応）
  - `name`: イベント名（日本語）
  - `type`: イベントタイプ
  - `displayType`: 表示タイプ（SIDESTORY等）
  - `startTime`: 開始時刻（UnixTimestamp）
  - `endTime`: 終了時刻（UnixTimestamp）
  - `hasStage`: ステージの有無

### ストーリーJSONファイル
- 各ストーリーファイルは以下の構造：
  - `lang`: 言語コード
  - `eventid`: イベントID
  - `eventName`: イベント名
  - `storyCode`: ストーリーコード
  - `storyName`: ストーリー名
  - `storyInfo`: ストーリー概要
  - `storyList`: ストーリー要素の配列

### storyList要素のタイプ
- `Dialog`: ダイアログボックスの表示/非表示
- `Character`: キャラクターの表示
- `name`: テキスト表示（地の文、キャラクター名付き会話）
  - `content`: 表示テキスト
  - `name`: キャラクター名（オプション）
- `Subtitle`: 字幕表示
- `Background`: 背景画像の変更
- `playMusic`/`stopmusic`: BGM制御
- `Blocker`: 画面フェード効果
- `Delay`/`delay`: 待機時間

## ストーリー表示順序と戦闘情報の改良

### 調査結果
ArknightsStoryJsonのデータ構造を詳しく調査した結果、以下の重要な発見がありました：

#### stage_table.jsonから分かる情報
- `unlockCondition`: 各ステージの解放条件（前のステージクリア要）
- `code`: ゲーム内表示コード（OR-1、OR-ST-1等）
- `stageType`: ステージタイプ（ACTIVITY等）
- `dangerLevel`: 推奨レベル表示
- `name`: ステージの正式名称

#### ストーリーファイルの正しい順序
- 戦闘ステージには `_beg.json`（戦闘前）と `_end.json`（戦闘後）が存在
- `st01`、`st02`、`st03`等のストーリー専用ステージが戦闘ステージの間に配置
- `unlockCondition`を追うことで正しい進行順序が判明

#### 具体的な改善点
1. **ストーリー表示順序の修正**
   - stage_table.jsonの`unlockCondition`を参照して正しい順序でソート
   - 戦闘前→戦闘後の順序を維持
   - ストーリー専用ステージを適切な位置に配置

2. **戦闘情報の表示追加**
   - 戦闘前/戦闘後の区別を明示
   - ステージ難易度（`dangerLevel`）の表示
   - ストーリー専用ステージの識別

### 改良実装プラン

#### フェーズ2追加: ストーリー順序システム改良
- [x] stage_table.jsonからステージ情報を取得する仕組み
  - [x] `src/lib/stage_parser.py` - stage_table.json解析
  - [x] ステージ情報とストーリーファイルの紐付け
  - [x] `unlockCondition`を参照した正しい順序決定アルゴリズム
- [x] ストーリー表示の改良
  - [x] 戦闘前後の明示（"戦闘前"、"戦闘後"ラベル）
  - [x] ストーリー専用ステージの識別（"間章"等）
  - [x] 推奨レベル情報の表示
- [x] イベントページでのストーリー一覧表示改良
  - [x] 正しい進行順序での表示
  - [x] 戦闘情報（難易度、タイプ）の併記

#### データ構造の詳細（追加）

##### stage_table.json
- `unlockCondition`: ステージ解放条件の配列
  - `stageId`: 前提となるステージID
  - `completeState`: 必要なクリア状態（"PASS"等）
- `code`: ゲーム内コード（"OR-1"、"OR-ST-1"等）
- `dangerLevel`: 推奨レベル（"LV.20"、"昇進1 LV.1"等）
- `stageType`: ステージの種類（"ACTIVITY"等）

##### ストーリーファイルの命名パターン
1. **戦闘ステージ**: 
   - `level_[eventId]_[stageNum]_beg.json` (戦闘前)
   - `level_[eventId]_[stageNum]_end.json` (戦闘後)
2. **ストーリー専用ステージ**:
   - `level_[eventId]_st[番号].json`

##### 表示順序決定アルゴリズム
```python
# 1. stage_table.jsonからunlockConditionを解析
# 2. 依存関係グラフを構築
# 3. トポロジカルソートで正しい順序を決定
# 4. _beg → _end の順序を保証
# 5. ストーリー専用ステージを適切な位置に配置
```

## UI/UX機能詳細

### ダークモード実装詳細
プロジェクト要件の「ナイトモード」として実装。完全な白黒を避け、目に優しい色彩設計を採用。

#### 色彩設計原則
- **背景色**: `#1a1a1a`（深い黒） → `#2d3748`（カード背景、適度なコントラスト）
- **テキスト色**: `#e2e8f0`（オフホワイト、完全な白を避ける）
- **アクセント色**: `#4299e1`（明るい青、リンクと重要要素）
- **境界線・装飾**: `#4a5568`（中間グレー）

#### CSS変数システム
```css
:root {
  --background-color: #f5f5f5;
  --text-color: #333;
  --card-background: #fff;
  --border-color: #ddd;
  /* 他の変数... */
}

[data-theme="dark"] {
  --background-color: #1a1a1a;
  --text-color: #e2e8f0;
  --card-background: #2d3748;
  --border-color: #4a5568;
  /* ダークモード用の値... */
}
```

#### 対応済み要素
- メインコンテンツ背景（`.story-content`）
- ダイアログブロック（`.dialog-block`）
- ボタン類（`.btn-primary`、`.btn-secondary`、`.btn-back`）
- ストーリーヘッダー（`.story-header h2`）
- 話者名（`.speaker`）
- ナビゲーション要素全般
- フォーム要素（検索入力、フィルター選択）

### フォント切り替え実装
プロジェクト要件の「フォント切り替え」機能として実装。

#### フォント選定
- **ゴシック体モード**: OS標準san-serif（`system-ui`, `-apple-system`, `'Segoe UI'`, `'Roboto'`等）
- **明朝体モード**: 読みやすいWebフォント
  - 日本語: `Noto Serif JP`（Google Fonts）
  - 欧文: `Crimson Text`（Google Fonts）
  - フォールバック: `'Georgia'`, `'Times New Roman'`, `'Yu Mincho'`等

## 注意事項
- ArknightsStoryJsonのライセンスを確認し、適切にクレジット表記を行う
- ストーリーデータの著作権に配慮する
- 定期的にsubmoduleを更新して最新のストーリーデータを反映する仕組みを検討
- Python 3.8以上を使用（型ヒントやf-stringなどの機能を活用）
- ストーリーファイル名のパターン：`level_[eventId]_[stageId].json`または`level_[eventId]_st[番号].json`
- stage_table.jsonを参照してストーリーの正しい進行順序を決定する
