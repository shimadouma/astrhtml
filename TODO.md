# TODO list for development

## プロジェクト概要
- アークナイツのストーリーをHTML化して Github Pages で公開する用のリポジトリを作成する
- アークナイツのストーリーデータは https://github.com/050644zf/ArknightsStoryJson を submodule として追加して参照する
  - 対象とするストーリーデータは ArknightsStoryJson/ja_JP/gamedata/story/activities にあるもの
  - ArknightsStoryJson/ja_JP/gamedata/story/activities の各ディレクトリがイベントに対応している
    - ディレクトリ名がイベントIDとなっていて、 ArknightsStoryJson/ja_JP/gamedata/excel/activity_table.json の basicInfo.<eventId> でイベントの基本情報（イベント名、開始日時、修了日時など）が取得できる

## 今後の機能拡張候補

### プログレッシブウェブアプリ（PWA）対応（実装見送り中）
- [ ] `static/manifest.json` - PWAマニフェスト
- [ ] `static/sw.js` - Service Worker
- [ ] オフライン対応
- [ ] インストール可能なアプリとしての機能

### パフォーマンス最適化
- [ ] 画像の遅延読み込み（Lazy Loading）
- [ ] ページネーション機能（大量のイベントがある場合）
- [ ] 仮想スクロール（長いストーリーページ）
- [ ] WebP画像形式のサポート

### アクセシビリティ改善
- [ ] スクリーンリーダー対応の強化
- [ ] キーボードナビゲーション改善
- [ ] ARIA属性の追加
- [ ] 高コントラストモード

### 追加機能検討
- [ ] ストーリー読了管理
- [ ] お気に入りイベント機能
- [ ] ストーリー内テキスト検索
- [ ] 共有機能（SNS連携）
- [ ] 印刷用スタイルシート

### 技術的改善
- [ ] TypeScript導入検討
- [ ] ユニットテストの追加
- [ ] E2Eテストの実装
- [ ] CI/CDパイプラインの改善
- [ ] ビルド時間の最適化

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
├── preview.py                 # ローカルプレビューサーバー
├── requirements.txt           # Python依存関係
├── .gitignore
├── .gitmodules
├── README.md
├── TODO.md
├── DONE.md                    # 完了したタスク
└── CLAUDE.md                  # Claude Code設定
```

## 注意事項
- ArknightsStoryJsonのライセンスを確認し、適切にクレジット表記を行う
- ストーリーデータの著作権に配慮する
- 定期的にsubmoduleを更新して最新のストーリーデータを反映する仕組みを検討
- Python 3.8以上を使用（型ヒントやf-stringなどの機能を活用）
- ストーリーファイル名のパターン：`level_[eventId]_[stageId].json`または`level_[eventId]_st[番号].json`
- stage_table.jsonを参照してストーリーの正しい進行順序を決定する
- ブックマーク機能はローカルストレージ使用のためブラウザ依存（プライバシー配慮）