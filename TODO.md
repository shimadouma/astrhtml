# TODO list for development

## プロジェクト概要
- アークナイツのストーリーをHTML化して Github Pages で公開する用のリポジトリを作成する
- アークナイツのストーリーデータは https://github.com/050644zf/ArknightsStoryJson を submodule として追加して参照する
  - 対象とするストーリーデータは ArknightsStoryJson/ja_JP/gamedata/story/activities にあるもの
  - ArknightsStoryJson/ja_JP/gamedata/story/activities の各ディレクトリがイベントに対応している
    - ディレクトリ名がイベントIDとなっていて、 ArknightsStoryJson/ja_JP/gamedata/excel/activity_table.json の basicInfo.<eventId> でイベントの基本情報（イベント名、開始日時、修了日時など）が取得できる
- メインストーリーのイベントも対象とする
  - メインストーリーは data/ArknightsStoryJson/ja_JP/gamedata/story/obt/main/ にjsonファイルがある
    - メインストーリーは章ごとにディレクトリが別れていないので、章ごとにデータを分けて、各メインストーリーの章ごとにイベントページを作成する
## 文字数表示機能（wordcount.json）実装計画

### 機能概要
- `data/ArknightsStoryJson/ja_JP/wordcount.json` に各イベントのステージの文字数一覧が記載されている
  - 各イベントページのストーリー一覧に文字数を表示する
  - 各ストーリーページのタイトルの下に文字数を表示する
  - イベントのストーリーの並び順は、 wordcount.json にある並び順にステージIDがある場合にはこれを優先して採用する

### データ構造
```json
{
  "イベントID": {
    "activities/イベントID/level_ファイル名": 文字数,
    ...
  }
}
```

### 実装計画

#### Phase 1: パーサー実装
- [ ] **src/lib/wordcount_parser.py** - wordcount.json解析モジュール作成
  - [ ] `load_wordcount_data()` - JSONファイルの読み込み
  - [ ] `get_story_wordcount(event_id, story_file)` - 特定ストーリーの文字数取得
  - [ ] `get_event_story_order(event_id)` - イベントのストーリー順序取得
  - [ ] `get_total_wordcount(event_id)` - イベント全体の文字数合計

#### Phase 2: 既存モジュール更新
- [ ] **src/lib/stage_parser.py** - 順序決定ロジック更新
  - [ ] `get_event_story_order()` にwordcount順序を優先する処理追加
  - [ ] wordcount.jsonに存在しない場合は既存ロジックにフォールバック
  
- [ ] **src/generators/event_generator.py** - イベントページ生成更新
  - [ ] 各ストーリーリンクに文字数を追加表示
  - [ ] イベント全体の合計文字数を表示
  
- [ ] **src/generators/story_generator.py** - ストーリーページ生成更新
  - [ ] ストーリータイトル下に文字数を表示

#### Phase 3: テンプレート更新
- [ ] **templates/event.html** - イベントページテンプレート
  - [ ] ストーリー一覧に文字数表示（例: "OR-1 (2,645文字)"）
  - [ ] 合計文字数の表示セクション追加
  
- [ ] **templates/story.html** - ストーリーページテンプレート
  - [ ] タイトル下に文字数バッジ表示

#### Phase 4: スタイリング
- [ ] **static/css/style.css** - 文字数表示用スタイル
  - [ ] 文字数バッジのデザイン
  - [ ] ストーリー一覧での文字数表示レイアウト

### 実装上の注意点
1. **ファイルパスのマッピング**: wordcount.jsonのパスと実際のストーリーファイルのマッピング処理
2. **メインストーリー対応**: メインストーリーもwordcount.jsonに含まれる場合の処理
3. **エラーハンドリング**: wordcount.jsonに存在しないストーリーの処理
4. **パフォーマンス**: 大量のイベントでも高速に動作するよう最適化

## メインストーリー実装計画

### データ構造分析結果
- **場所**: `data/ArknightsStoryJson/ja_JP/gamedata/story/obt/main/`
- **ファイル数**: 353ファイル（15章分：00〜14）
- **ファイル命名規則**:
  - `level_main_XX-YY_beg.json` - 戦闘前ストーリー
  - `level_main_XX-YY_end.json` - 戦闘後ストーリー
  - `level_st_XX-YY.json` - 間章
  - `level_spst_XX-YY.json` - 特別間章
- **ゾーンデータ**: zone_table.jsonに`main_0`〜`main_14`として存在
  - zoneNameFirst: 章タイトル（例：「序章」「第十四章」）
  - zoneNameSecond: サブタイトル（例：「暗黒時代・上」「慈悲光塔」）
  - zoneNameThird: エピソード番号（例：「EPISODE 00」）

### 実装フェーズ

#### フェーズ1: コア機能実装
- [x] **データモデル拡張**
  - [x] `src/models/zone_info.py` - メインストーリー章情報モデル作成
  - [ ] `src/models/activity_info.py` - メインストーリー対応の拡張
  
- [x] **パーサー実装**
  - [x] `src/lib/zone_parser.py` - zone_table.jsonからメインストーリー章情報を取得
  - [x] `src/lib/main_story_parser.py` - メインストーリーファイルの解析と章ごとの分類
  - [x] `src/lib/stage_parser.py` - メインストーリーステージ順序の決定ロジック追加
    - [x] メインストーリー用の`get_main_story_order_for_chapter()`関数追加
    - [ ] 間章（st_XX, spst_XX）の適切な配置ロジック実装
    - [ ] トポロジカルソート実装でステージ依存関係を解決
  
- [x] **ジェネレーター更新**
  - [x] `src/generators/main_story_generator.py` - メインストーリー章ページ生成
  - [x] `src/generators/index_generator.py` - ホームページにメインストーリーセクション追加
  - [ ] `src/generators/story_generator.py` - メインストーリー対応

#### フェーズ2: ビルドシステム統合
- [x] **build.py更新**
  - [x] メインストーリー処理オプション追加（`--include-main`, `--main-only`）
  - [x] 章単位でのビルド制限オプション（`--main-chapters 0,1,2`）
  
- [ ] **設定ファイル**
  - [ ] `src/config.py` - メインストーリー関連設定追加
    - メインストーリーパス設定
    - ~~章情報マッピング~~（動的検出のため不要）
    - ビルドオプションのデフォルト値
    - 章番号の検出・ソート設定

#### フェーズ3: UI/UX改善
- [x] **テンプレート更新**
  - [x] `templates/index.html` - メインストーリーセクション追加
  - [x] `templates/main_story_index.html` - メインストーリー章ページテンプレート作成
  - [x] `templates/main_story_chapter.html` - メインストーリー章詳細ページテンプレート作成
  - [ ] `templates/components/main_nav.html` - メインストーリー専用ナビゲーション
  
- [x] **スタイリング**
  - [x] `static/css/main_story.css` - メインストーリー専用スタイル
  - [ ] 章番号バッジのデザイン
  - [ ] エピソード進行状況表示

### 実装詳細

#### 1. ディレクトリ構造
```
dist/
├── events/           # 既存イベント
├── main/            # メインストーリー
│   ├── chapter_00/  # 序章
│   │   ├── index.html
│   │   └── stories/
│   │       ├── main_00-01_beg.html
│   │       ├── main_00-01_end.html
│   │       └── ...
│   ├── chapter_01/  # 第一章
│   └── ...
```

#### 2. URL構造
- 章一覧: `/main/index.html`
- 各章: `/main/chapter_XX/index.html`
- ストーリー: `/main/chapter_XX/stories/main_XX-YY_[beg|end].html`

#### 3. データ処理フロー
1. zone_table.jsonから章情報を取得
2. メインストーリーファイルを章ごとに分類
3. stage_table.jsonから依存関係を解析
4. 章ごとにストーリー順序を決定
5. HTMLファイルを生成

#### 4. メインストーリー順序決定方法

**ステージ順序の決定**:
- stage_table.jsonの`unlockCondition`を使用して依存関係を構築
- 例: `main_01-02`は`main_01-01`の完了が必要
- 各章の最初のステージ（例: `main_XX-01`）はunlockCondition = []

**ファイル命名パターンとマッピング**:
- `level_main_XX-YY_beg.json` → ステージ`main_XX-YY`の戦闘前ストーリー
- `level_main_XX-YY_end.json` → ステージ`main_XX-YY`の戦闘後ストーリー  
- `level_st_XX-YY.json` → ステージ`st_XX-YY`の間章（特定ステージ完了後に開放）
- `level_spst_XX-YY.json` → ステージ`spst_XX-YY`の特別間章

**順序決定アルゴリズム**:
1. 章内の全ステージをstage_table.jsonから抽出（`main_XX-*`, `st_XX-*`, `spst_XX-*`）
2. unlockConditionによる依存関係グラフを構築
3. トポロジカルソートで正しい順序を決定
4. 各ステージについて：
   - 戦闘前ストーリー（`_beg`）があれば先に表示
   - 戦闘後ストーリー（`_end`）があれば後に表示
   - 間章は依存ステージ完了後の適切な位置に配置

**具体例（第5章）**:
```
1. main_05-01_beg → main_05-01_end
2. main_05-02_beg → main_05-02_end
...
10. main_05-10_beg → main_05-10_end
11. st_05-01 (main_05-10完了後に開放される間章)
```

**特別な考慮事項**:
- 第0章: 一部ステージはチュートリアル（tr_XX）完了が前提
- 間章（st_XX-YY）: 通常ステージとは独立したストーリー、特定ステージ完了後に開放
- 特別間章（spst_XX-YY）: より特殊なストーリー、開放条件が複雑な場合あり

#### 5. 後方互換性
- 既存のイベントシステムとの共存
- ブックマークデータ構造の互換性維持
- URLパターンの衝突回避

### テスト計画
- [ ] 単体テスト
  - [ ] zone_parser.pyのテスト
  - [ ] main_story_parser.pyのテスト
  - [ ] ストーリー順序決定ロジックのテスト
  
- [ ] 統合テスト
  - [ ] 小規模データでのビルドテスト（章0のみ）
  - [ ] 全章ビルドテスト
  - [ ] ブックマーク機能の動作確認
  
- [ ] パフォーマンステスト
  - [ ] 353ファイルの処理時間測定
  - [ ] メモリ使用量の監視
  - [ ] ビルド最適化の検討

### 実装優先順位
1. **必須**: コア機能（パーサー、ジェネレーター）
2. **重要**: ビルドシステム統合
3. **推奨**: UI/UX改善
4. **オプション**: 進行状況表示、章間リンク

### 新章追加への対応設計

**自動検出・動的対応**:
- zone_table.jsonから動的に章一覧を検出（`main_0`〜`main_N`パターン）
- 新章が追加されても設定ファイル変更不要
- ビルド時に存在する章のみを自動処理

**スケーラブルな実装**:
```python
# 動的章検出の例
def get_available_main_chapters(zone_data: dict) -> List[int]:
    """zone_table.jsonから利用可能な章番号を動的取得"""
    chapters = []
    for zone_id in zone_data.get('zones', {}).keys():
        if zone_id.startswith('main_') and zone_id.replace('main_', '').isdigit():
            chapter_num = int(zone_id.replace('main_', ''))
            chapters.append(chapter_num)
    return sorted(chapters)
```

**URL設計の拡張性**:
- `/main/chapter_XX/` 形式で章番号に上限なし
- 15章以降（chapter_15, chapter_16...）も同じ規則で対応
- ナビゲーションも動的生成で自動対応

**ビルドシステムの柔軟性**:
```bash
# 新章のみビルド
python3 build.py --main-chapters 15,16

# 最新N章のみビルド  
python3 build.py --main-latest 5

# 全章自動検出ビルド
python3 build.py --include-main
```

**UI表示の動的対応**:
- 章一覧ページで利用可能章を自動表示
- 章番号の桁数増加（3桁等）にも対応
- ソート順序は数値順で自動調整

**データ構造の前方互換性**:
- ZoneInfo モデルで章番号の型制限なし
- JSON出力でも章番号は文字列として保存
- ブックマークのURL形式も章番号制限なし

### 注意事項
- メインストーリーは継続的に更新される（新章追加）
- ファイル数が多いため、開発時は章単位でテスト
- zone_table.jsonの構造変更に注意
- ストーリー間の依存関係を正確に処理
- **新章追加時の自動対応**: 設定変更やコード修正なしで新章を認識
- **GitHub Actions**: 新章追加時も既存のワークフローで自動ビルド・デプロイ

## 今後の機能拡張候補

### プログレッシブウェブアプリ（PWA）対応（実装見送り中）
- [ ] `static/manifest.json` - PWAマニフェスト
- [ ] `static/sw.js` - Service Worker
- [ ] オフライン対応
- [ ] インストール可能なアプリとしての機能

### アクセシビリティ改善
- [ ] スクリーンリーダー対応の強化
- [ ] キーボードナビゲーション改善
- [ ] ARIA属性の追加
- [ ] 高コントラストモード

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

## MINISTORY イベント特殊仕様

### 重要な設計情報
**MINISTORY形式のイベントは攻略用ステージとシナリオ用ステージが分離されている**

#### ステージ構造の分離
1. **攻略用ステージ（処理対象外）**:
   - stage_table.jsonに定義されている戦闘用ステージ
   - 例：`act15mini_01` (FD-1), `act15mini_02` (FD-2), `act15mini_s01` (FD-S-1) など
   - プレイヤーが攻略するゲームプレイ用ステージ
   - **これらは処理の対象外とする**

2. **シナリオ用ステージ（処理対象）**:
   - story/activities/[eventId]/level_[eventId]_st*.json ファイル
   - 例：`level_act15mini_st01.json`, `level_act15mini_st02.json` など
   - ストーリーコンテンツのみを含む
   - **これらのみを処理対象とする**

#### 具体例（act15mini）
```
攻略用ステージ（無視）:
- act15mini_01 → FD-1: 繫栄滋養
- act15mini_02 → FD-2: 辺境警邏  
- act15mini_s01 → FD-S-1: 凍土境域
...

シナリオ用ステージ（処理対象）:
- level_act15mini_st01.json → 対応するシナリオ専用ステージ
- level_act15mini_st02.json → 対応するシナリオ専用ステージ
...
```

### 実装上の注意点
- MINISTORYイベントの場合、`level_*_st*.json` ファイルのみを処理する
- 攻略用ステージとのマッピングは行わない
- シナリオ用ステージ専用の順序決定ロジックが必要
- 他のイベントタイプ（SIDESTORY等）には影響しない設計とする


### 実装計画


#### Phase 3: 実装詳細

##### 3.1 専用関数の実装
```python
def get_ministory_stages(event_id: str, story_files: List[str]) -> List[Tuple[str, Dict]]:
    """
    MINISTORY専用: ストーリーファイルのみから仮想ステージ情報を生成
    攻略用ステージは完全に無視
    """
    pass

def is_ministory_story_file(file_name: str) -> bool:
    """
    MINISTORYのストーリーファイル判定（level_*_st*.json）
    """
    pass
```

##### 3.2 処理フロー変更
1. **イベントタイプ判定**: `event_type == 'MINISTORY'`
2. **ストーリーファイルのみ処理**: `level_*_st*.json` ファイルを対象
3. **攻略ステージ除外**: stage_table.jsonの攻略ステージは参照しない
4. **シンプルな順序決定**: ファイル名の番号順（st01, st02...）



### 影響範囲
- **修正対象**: `src/lib/stage_parser.py`, `src/lib/event_parser.py`
- **影響イベント**: act10mini〜act17mini等のMINISTORY形式イベント
- **処理方針**: シナリオ用ステージ（`level_*_st*.json`）のみを処理対象とする

## ストーリーリンク問題の修正履歴

### 2025-08-10: 主要なストーリーリンク問題を修正

**問題**: イベントページでストーリーファイルが生成されているが、イベントインデックスページでリンクされていない

**原因分析**:
1. **ステージID検出の問題**: 一部のイベント（act3d0等）でevent_idとstage_idのプレフィックスが一致しない
2. **ストーリーファイル名マッピングの問題**: `level_act4d0_st01.json`のようなファイル名が`act4d0_01`ステージに正しくマッピングされない

**実装した修正**:
1. **`get_event_related_stages()`関数の追加** (`src/lib/stage_parser.py`):
   - Method 1: 直接的なstage_idプレフィックスマッチング
   - Method 2: levelIdパターンマッチングで不一致なevent/stage IDを処理
   - Method 3: 特殊ケースマッピング（act3d0 → a003_*）

2. **ストーリーファイル名→ステージIDマッピングの改善**:
   - `level_actXXX_st01.json` → `actXXX_01`パターンの処理
   - act3d0の特殊なa003_*ステージIDパターンへの対応
   - 既存のMINISTORYロジックとの互換性維持

**修正結果**:
- **修正前**: 4つのイベントで完全にリンクなし (act3d0, act4d0, act6d5, act7d5)
- **修正後**: 全ての重要なストーリーリンク問題を解決
- **検証**: `scripts/check_empty_events.py`で確認済み

**影響を受けたファイル**:
- `src/lib/stage_parser.py` - ステージ検出とマッピングロジック
- `src/generators/event_generator.py` - イベントページ生成（既存コードは変更なし）

**注意**: 残りの「未リンク」項目は主に`ENTRY.html`や`story_*.html`などの特殊ケースファイルで、コアストーリーリンク機能は正常に動作中。

### 2025-08-10: ST（ストーリー）ステージリンク問題の修正

**問題**: 大部分のイベント（39個のイベント）でST（ストーリー）ステージ（*-ST-1.html、*-ST-2.html等）が生成されているが、イベントインデックスページでリンクされていない

**原因分析**:
- **STステージマッピングの誤り**: `level_actXXside_st01.json` → `actXXside_st01` ステージIDへのマッピングが正しく動作していない
- **既存の変換ロジックの問題**: 全てのSTファイルで `_st01` → `_01` の変換が適用されていたが、これは特定のイベント（act4d0、act6d5、act7d5）のみに適用されるべき

**実装した修正**:
1. **STステージマッピングロジックの修正** (`src/lib/stage_parser.py:266-283`):
   - 条件分岐を追加して、特定のTYPE_ACT4D0イベント（`act4d0`, `act6d5`, `act7d5`）のみで `st01` → `01` 変換を適用
   - その他のイベントでは `_st` プレフィックスを保持：`actXXside_st01` など

2. **修正内容**:
   ```python
   # 修正前: 全てのイベントでst->数値変換
   stage_id = f"{event_part}_{stage_num.zfill(2)}"
   
   # 修正後: 条件分岐による適切な変換
   if event_id in ['act4d0', 'act6d5', 'act7d5']:
       stage_id = f"{event_part}_{stage_num.zfill(2)}"  # st01 -> 01
   else:
       stage_id = f"{event_part}_st{stage_num.zfill(2)}" # st01 -> st01 (保持)
   ```

**修正結果**:
- **修正前**: 39個のイベントでSTステージがリンクされていない（例：OR-ST-1.html、EP-ST-2.html等）
- **修正後**: 全てのSTステージが正常にリンクされる
- **検証**: 20個のイベントビルドでテスト済み、全て✅で成功

**影響範囲**:
- **修正ファイル**: `src/lib/stage_parser.py`のみ
- **影響イベント**: SIDESTORY形式の大部分のイベント（actXXside、actXXmini以外）
- **テスト済み**: act40side、act39side、act38side等で動作確認済み

**重要**: この修正により、イベントストーリーの完全性が大幅に改善され、ユーザーは全てのストーリーコンテンツに適切にアクセス可能になった。


## 注意事項
- ArknightsStoryJsonのライセンスを確認し、適切にクレジット表記を行う
- ストーリーデータの著作権に配慮する
- 定期的にsubmoduleを更新して最新のストーリーデータを反映する仕組みを検討
- Python 3.8以上を使用（型ヒントやf-stringなどの機能を活用）
- ストーリーファイル名のパターン：`level_[eventId]_[stageId].json`または`level_[eventId]_st[番号].json`
- stage_table.jsonを参照してストーリーの正しい進行順序を決定する
- ブックマーク機能はローカルストレージ使用のためブラウザ依存（プライバシー配慮）