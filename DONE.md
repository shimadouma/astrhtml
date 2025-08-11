# DONE - Completed Tasks

This file contains completed features and improvements from TODO.md

## プロジェクト初期セットアップ (Completed: 2024)
- [x] プロジェクトの基本構造を作成
  - [x] requirements.txtの作成（Python依存パッケージ）
  - [x] .gitignoreの作成
  - [x] .gitmodulesの設定
- [x] ArknightsStoryJsonをsubmoduleとして追加
- [x] Python仮想環境のセットアップ

## データ処理レイヤー (Completed: 2024)
- [x] データモデルの定義
  - [x] `src/models/story.py` - ストーリーデータのクラス定義
  - [x] `src/models/event.py` - イベントデータのクラス定義
  - [x] `src/models/activity.py` - activity_tableデータのクラス定義
- [x] データ読み込みモジュール
  - [x] `src/lib/data_loader.py` - JSONファイル読み込み処理
  - [x] `src/lib/event_parser.py` - イベント情報のパース処理
  - [x] `src/lib/story_parser.py` - ストーリーデータのパース処理
- [x] データ処理ユーティリティ
  - [x] `src/utils/date_formatter.py` - 日付フォーマット処理
  - [x] `src/utils/text_processor.py` - テキスト処理
  - [x] `src/utils/story_renderer.py` - ストーリー要素のHTML変換処理
  - [x] `src/utils/file_utils.py` - ファイル操作ユーティリティ

## HTML生成システム (Completed: 2024)
- [x] テンプレートエンジン（Jinja2）の設定
  - [x] `templates/base.html` - ベーステンプレート
  - [x] `templates/index.html` - インデックスページテンプレート
  - [x] `templates/event.html` - イベントページテンプレート
  - [x] `templates/story.html` - ストーリーページテンプレート
- [x] スタイルシート
  - [x] `static/css/main.css` - メインスタイル
  - [x] `static/css/story.css` - ストーリー表示用スタイル
- [x] HTML生成モジュール
  - [x] `src/generators/index_generator.py` - インデックスページ生成
  - [x] `src/generators/event_generator.py` - イベントページ生成
  - [x] `src/generators/story_generator.py` - ストーリーページ生成
  - [x] `src/generators/base_generator.py` - 基底ジェネレータクラス
- [x] ストーリー表示の改良
  - [x] 背景画像情報を非表示にする機能実装
  - [x] 同じ話者の連続する台詞を統合する機能実装

## ビルドシステム (Completed: 2024)
- [x] メインビルドスクリプト
  - [x] `build.py` - メインビルド処理
  - [x] `src/config.py` - ビルド設定
- [x] 出力ディレクトリ構造の実装
- [x] コマンドラインインターフェース
  - [x] `python build.py` - 全体ビルド
  - [x] `python build.py --limit` - 限定ビルド
  - [x] `python build.py --clean` / `--no-clean` - ビルド制御

## GitHub Pages デプロイメント (Completed: 2024)
- [x] GitHub Actionsワークフローの作成
  - [x] `.github/workflows/deploy.yml` - 自動デプロイ設定
- [x] GitHub Pages設定
- [x] デプロイスクリプト
  - [x] `scripts/deploy.sh` - 手動デプロイ用スクリプト

## ドキュメント整備 (Completed: 2024)
- [x] README.mdの更新
  - [x] プロジェクト概要
  - [x] 必要な環境・依存関係
  - [x] セットアップ手順
  - [x] ビルド・デプロイ手順
  - [x] GitHub Pages設定方法

## 機能拡張 (Completed: 2024-2025)

### 検索機能 (Completed: 2024)
- [x] `static/js/search.js` - クライアントサイド検索
- [x] `src/generators/search_index.py` - 検索インデックス生成
- [x] 検索データの自動生成（events, stories）
- [x] リアルタイム検索とハイライト機能

### フィルタリング機能 (Completed: 2024)
- [x] `static/js/filters.js` - イベントタイプと年別フィルタ
- [x] 検索との連携機能

### ダークモード対応 (Completed: 2024)
- [x] `static/js/theme.js` - テーマ切り替え機能
- [x] CSS変数を使ったダーク/ライトテーマ
- [x] LocalStorageでの設定保存
- [x] ダークモード色彩の改善・調整
  - [x] 背景色とテキスト色のコントラスト調整
  - [x] カード背景色の統一
  - [x] ストーリーページの完全ダークモード対応
  - [x] リンク色の可読性向上
  - [x] ボタン類の色調整
  - [x] ストーリーヘッダーの色調整
  - [x] 話者名の色調整
  - [x] 各種UI要素の統一感のある色設定

### フォント切替機能 (Completed: 2024)
- [x] `static/js/font.js` - フォント切り替え機能
- [x] ゴシック体モード（OS標準san-serif）
- [x] 明朝体モード（Noto Serif JP, Crimson Text）
- [x] LocalStorageでの設定保存
- [x] ヘッダーにフォント切替トグルボタン追加
- [x] CSS変数を使ったフォントファミリー制御
- [x] レスポンシブ対応

### UI/UX改善 (Completed: 2024)
- [x] ヘッダーレイアウト最適化
- [x] ナビゲーションメニューの折り返し対策
- [x] ブックマーク機能のUX向上

### プレビューサーバー (Completed: 2024)
- [x] `preview.py` - ローカル開発サーバスクリプト
- [x] 自動ブラウザ起動機能
- [x] 静的ファイル配信
- [x] ポート番号設定（デフォルト8000）
- [x] CORS対応とセキュリティ設定
- [x] サーバー安定性改善

### ブックマーク機能 (Completed: 2024-2025)
- [x] `static/js/bookmark.js` - ブックマーク管理機能
- [x] ローカルストレージでのブックマーク保存
- [x] ストーリーページでの台詞ブロックブックマーク
- [x] ナビゲーションメニューからのブックマーク一覧表示
- [x] ブックマーク一覧ページ生成機能
- [x] ブックマーク削除・管理機能
- [x] クリック式ブックマーク操作
- [x] ブックマークインジケーター表示
- [x] ブックマークページでの検索・フィルタ・エクスポート・インポート機能
- [x] データ互換性保証

### プロジェクト設定 (Completed: 2024)
- [x] CLAUDE.mdにデータ互換性ガイドライン追加
- [x] ブックマークデータのバージョニング・移行対応ルール策定

### ストーリー順序システム改良 (Completed: 2024)
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

## バグ修正 (2025)
- [x] Zone ID不一致によるストーリーリスト空表示問題の修正 (2025-08-09)
  - stage_idとevent_idのマッチング方法を改善
  - ミニイベントおよび古いイベントの表示問題を解決
- [x] ストーリーヘッダーのレイアウト問題修正 (2025-08-09)
  - story-infoの段落がインライン表示される問題を修正
  - CSS競合の解決とスコープの適切な設定

## メインストーリー実装 (Completed: 2025-08-10)

### フェーズ1: コア機能実装
- [x] **データモデル拡張**
  - [x] `src/models/zone_info.py` - メインストーリー章情報モデル作成
  
- [x] **パーサー実装**
  - [x] `src/lib/zone_parser.py` - zone_table.jsonからメインストーリー章情報を取得
  - [x] `src/lib/main_story_parser.py` - メインストーリーファイルの解析と章ごとの分類
  
- [x] **ジェネレーター更新**
  - [x] `src/generators/main_story_generator.py` - メインストーリー章ページ生成
  - [x] `src/generators/index_generator.py` - ホームページにメインストーリーセクション追加

### フェーズ2: ビルドシステム統合
- [x] **build.py更新**
  - [x] メインストーリー処理オプション追加（`--include-main`, `--main-only`）
  - [x] 章単位でのビルド制限オプション（`--main-chapters 0,1,2`）

### フェーズ3: UI/UX改善
- [x] **テンプレート更新**
  - [x] `templates/index.html` - メインストーリーセクション追加
  - [x] `templates/main_story_index.html` - メインストーリー章ページテンプレート作成
  - [x] `templates/main_story_chapter.html` - メインストーリー章詳細ページテンプレート作成
  
- [x] **スタイリング**
  - [x] `static/css/main_story.css` - メインストーリー専用スタイル

## MINISTORY イベント特殊仕様対応 (Completed: 2025-08-10)

### Phase 1: 基本修正
- [x] `get_story_order_for_event()`でMINISTORY特別処理追加
- [x] ファイル名→ステージIDマッピング修正
- [x] イベントタイプ検出ロジック追加

### Phase 2: シナリオ専用ステージ処理の実装
- [x] **stage_parser.pyの専用ロジック追加**:
  - [x] `get_ministory_stages()` 関数追加 - シナリオステージのみを抽出
  - [x] `is_ministory_story_file()` 関数追加 - MINISTORYストーリーファイル判定
  - [x] `get_story_order_for_event()` でMINISTORY用の分岐処理追加
  - [x] 攻略用ステージを完全に除外し、ストーリーファイルベースで処理

- [x] **シナリオステージの順序決定ロジック**:
  - [x] story fileの命名規則（st01, st02...）による順序決定
  - [x] stage_table.jsonの攻略ステージに依存しない独立した順序決定
  - [x] 仮想ステージ情報（ST-1, ST-2...）の生成

## TYPE_ACT4D0 イベント特殊仕様対応 (Completed: 2025-08-10)

### 問題背景
TYPE_ACT4D0 イベント（act4d0, act6d5, act7d5）は MINISTORY イベントと同様に、攻略用ステージとストーリー用ステージが分離されているが、従来の処理では攻略用ステージが表示されていた。また「ストーリーなし」表示問題も発生していた。

### 実装した修正

#### Phase 1: ステージ表示の修正
- [x] **`handle_type_act4d0_events()` 関数の実装** (`src/lib/stage_parser.py`)
  - [x] 攻略用ステージ（SW-EV-*, AF-*, SA-*）の表示を停止
  - [x] ストーリー用ステージ（ST-1, ST-2...）の仮想ステージ生成
  - [x] MINISTORY イベントと同様の処理ロジック適用

#### Phase 2: ストーリーリンク問題の修正
- [x] **ファイル名マッピング問題の解決**
  - [x] JSON ファイル名（level_act4d0_st01.json）と HTML ファイル名（story_0.html）の一貫したマッピング
  - [x] stage_parser は JSON ファイル名を返し、event/story generator が HTML ファイル名を処理
  - [x] 0-based インデックスによる正確なファイル名生成

- [x] **event_generator.py の TYPE_ACT4D0 対応**
  - [x] MINISTORY イベントと同様のストーリーマッチング処理
  - [x] ファイルインデックスベースの HTML ファイル名生成（story_0, story_1, etc.）
  - [x] イベントタイプ表示を "MINISTORY" に統一

- [x] **story_generator.py の TYPE_ACT4D0 対応**
  - [x] 0-based インデックスによる HTML ファイル名生成
  - [x] 既存の MINISTORY 処理との統合

#### Phase 3: ストーリータイトル表示の改善
- [x] **実際のストーリータイトル表示**
  - [x] JSON ファイルの `storyName` フィールドからタイトル抽出
  - [x] 汎用的な「シナリオ 1」形式から実際のタイトルに変更
  - [x] イベントページでの適切なタイトル表示

### 修正結果
- **対象イベント**: act4d0, act6d5, act7d5
- **修正前**: 攻略用ステージ表示、「ストーリーなし」表示、汎用的なタイトル
- **修正後**: ストーリー用ステージのみ表示、適切なリンク、実際のストーリータイトル
- **技術的改善**: ファイル名マッピングの一貫性、コンポーネント間の適切な役割分担

## 文字数表示機能（wordcount.json）実装 (Completed: 2025-08-11)

### Phase 1: パーサー実装
- [x] **src/lib/wordcount_parser.py** - wordcount.json解析モジュール作成
  - [x] `load_wordcount_data()` - JSONファイルの読み込み
  - [x] `get_story_wordcount(event_id, story_file)` - 特定ストーリーの文字数取得
  - [x] `get_event_story_order(event_id)` - イベントのストーリー順序取得
  - [x] `get_total_wordcount(event_id)` - イベント全体の文字数合計

### Phase 2: 既存モジュール更新
- [x] **src/lib/stage_parser.py** - 順序決定ロジック更新
  - [x] `get_event_story_order()` にwordcount順序を優先する処理追加
  - [x] wordcount.jsonに存在しない場合は既存ロジックにフォールバック
  
- [x] **src/generators/event_generator.py** - イベントページ生成更新
  - [x] 各ストーリーリンクに文字数を追加表示
  - [x] イベント全体の合計文字数を表示
  
- [x] **src/generators/story_generator.py** - ストーリーページ生成更新
  - [x] ストーリータイトル下に文字数を表示

### Phase 3: テンプレート更新
- [x] **templates/event.html** - イベントページテンプレート
  - [x] ストーリー一覧に文字数表示（例: "2,645文字"）
  
- [x] **templates/story.html** - ストーリーページテンプレート
  - [x] タイトル下に文字数バッジ表示

### Phase 4: スタイリング
- [x] **static/css/story.css** - 文字数表示用スタイル
  - [x] 文字数バッジのデザイン
  - [x] ストーリー一覧での文字数表示レイアウト

## バグ修正 (2025-08-11)

### act9d0 DM-7/DM-8 仮想ストーリーリンク修正
- [x] **問題**: wordcount.json使用時にDM-7とDM-8が未リンク
- [x] **原因**: wordcount.jsonにこれらのステージのストーリーファイルが存在しない
- [x] **修正**: `get_story_order_from_wordcount()`に仮想ストーリーエントリ追加ロジック実装
- [x] **影響**: act9d0のすべてのステージが正常にリンクされるように

## UI/UX改善 (2025-08-11)

### ストーリーサマリー表示の改善
- [x] **イベントページ**: ストーリーサマリー（div.story-summary）を削除
- [x] **ストーリーページ**: サマリーをトグル可能に
  - [x] デフォルトで非表示（ネタバレ防止）
  - [x] 「あらすじを表示」ボタンで表示/非表示切り替え
  - [x] JavaScript関数とCSSスタイル追加