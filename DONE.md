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