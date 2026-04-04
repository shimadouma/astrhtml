# ArknightsStoryJson Data Structure Reference

This document describes the data structure of the [ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson) repository, used as the data source for this project. Data is located at `data/ArknightsStoryJson/ja_JP/`.

## Directory Structure

```
data/ArknightsStoryJson/ja_JP/
├── chardict.json              # Character code name -> display name mapping
├── charinfo.json              # Detailed character information and stories
├── extrastory.json            # Hidden/extra story entries
├── storyinfo.json             # Story summaries/plot descriptions
├── wordcount.json             # Word count statistics per story
└── gamedata/
    ├── excel/                 # Game data tables
    │   ├── zone_table.json    # Zone/chapter definitions
    │   ├── stage_table.json   # Stage/level definitions
    │   ├── activity_table.json# Event/activity definitions
    │   ├── story_table.json   # Story trigger/progression system
    │   └── ...
    └── story/                 # Story JSON files (dialogue/narrative)
        ├── obt/               # Persistent stories
        │   ├── guide/         # Tutorial stories
        │   ├── main/          # Main story chapters (00-16+)
        │   ├── memory/        # Operator memory stories
        │   └── rogue/         # Roguelike stories
        └── activities/        # Event stories
            ├── a001/
            ├── act10d5/
            ├── act45side/
            └── ...
```

## Excel Data Tables

### zone_table.json

Defines zones (chapters, event areas, resource stages).

**Root structure**: `{ "zones": { "<zone_id>": { ... }, ... } }`

#### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `zoneID` | string | Unique zone identifier | `"main_0"`, `"act2mainss_zone1"` |
| `zoneIndex` | int | Display order **within group** (NOT global chapter number) | `0`, `1`, `2` |
| `type` | string | Zone type | `"MAINLINE"`, `"MAINLINE_ACTIVITY"` |
| `zoneNameFirst` | string | Primary name | `"序章"`, `"Dissociative Recombination"` |
| `zoneNameSecond` | string | Secondary name/subtitle | `"暗黒時代・上"`, `"解離結合"` |
| `zoneNameTitleCurrent` | string | Episode number display | `"00"`, `"15"` |
| `zoneNameTitleEx` | string | Episode type label | `"EPISODE"` |
| `zoneNameThird` | string | Full episode display | `"EPISODE 00"` |
| `lockedText` | string | Unlock requirement text | `"前章クリアで開放"` |
| `canPreview` | bool | Whether story is previewable before unlock | `true` |
| `antiSpoilerId` | string? | Spoiler protection zone reference | `"main_15"` |
| `sixStarMilestoneGroupId` | string? | Achievement group ID | `"main_15"` |
| `bindMainlineZoneId` | string? | Link to temporary event version | `null` |
| `bindMainlineRetroZoneId` | string? | Link to permanent/retro version | `"permanent_main_1_zone1"` |

#### Zone Types

| Type | Description | Zone ID pattern | Chapters |
|------|-------------|-----------------|----------|
| `MAINLINE` | Standard main story chapters | `main_0` ~ `main_14` | 0-14 |
| `MAINLINE_ACTIVITY` | Time-limited main story events | `act2mainss_zone1`, `act3mainss_zone1` | 15, 16 |
| `MAINLINE_RETRO` | Permanent copy of MAINLINE_ACTIVITY | `permanent_main_1_zone1`, etc. | - |
| `WEEKLY` | Weekly resource stages | various | - |
| `CAMPAIGN` | Campaign/special event zones | various | - |
| `SIDESTORY` | Permanent side story zones | various | - |

#### Important Notes

- **`zoneIndex` is NOT the global chapter number.** It resets across groups (e.g., chapters 0-3 have index 0-3, chapters 4-8 have index 0-4, chapters 9-14 have index 0-5). The actual chapter number must be derived from the zone_id suffix (`main_N`) or `zoneNameTitleCurrent`.
- **Chapters 15+ use `MAINLINE_ACTIVITY`** type instead of `MAINLINE`. Their zone IDs don't follow the `main_N` pattern. Chapter number must be read from `zoneNameTitleCurrent`.
- **`zoneNameFirst`/`zoneNameSecond` field usage differs by type**: For `MAINLINE`, `first` = Japanese chapter label (e.g., "第一章"), `second` = subtitle (e.g., "暗黒時代・下"). For `MAINLINE_ACTIVITY`, `first` = English title, `second` = Japanese subtitle.

---

### stage_table.json

Defines all stages/levels including battle stages, story-only stages, and tutorials.

**Root structure**: `{ "stages": { "<stage_id>": { ... }, ... } }`

#### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `stageId` | string | Unique stage identifier | `"main_00-01"`, `"st_05-01"` |
| `stageType` | string | Stage category | `"MAIN"` |
| `difficulty` | string | Difficulty level | `"NORMAL"`, `"FOUR_STAR"` |
| `code` | string | Display stage code | `"0-1"`, `"EG-3"`, `"M8-1"` |
| `name` | string | Stage name (Japanese) | `"崩落"` |
| `description` | string | Stage description/hint | `"..."` |
| `zoneId` | string | Parent zone ID | `"main_0"` |
| `levelId` | string? | Links to story file path | `"Obt/Main/level_main_00-01"` |
| `dangerLevel` | string | Difficulty display text | `"LV.1"`, `"-"` |
| `isStoryOnly` | bool | Story-only (no battle rewards) | `false`, `true` |
| `hardStagedId` | string? | Hard mode counterpart | `"main_00-01#f#"` |
| `unlockCondition` | array | Prerequisites | See below |
| `apCost` | int | Stamina cost | `6`, `0` |
| `expGain` | int | Experience reward | `60` |

#### unlockCondition Structure

```json
[
    {
        "stageId": "main_02-08",
        "completeState": "PASS"
    }
]
```

- `stageId`: Stage that must be cleared first
- `completeState`: Required state (`"PASS"` or `"COMPLETE"`)

#### Stage ID Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `main_XX-YY` | Main story battle stage | `main_00-01`, `main_15-15` |
| `main_XX-YY#f#` | Hard mode variant | `main_00-01#f#` |
| `st_XX-YY` | Side/interlude story stage (story-only) | `st_05-01`, `st_15-02` |
| `spst_XX-YY` | Special interlude stage (story-only) | `spst_08-01`, `spst_16-03` |
| `tr_XX` | Tutorial stage | `tr_01`, `tr_27` |
| `sub_XX-YY` | Sub/supply stage | `sub_02-01` |
| `actXXd5_YY` | Event battle stage | `act10d5_01` |
| `actXXside_YY` | Side story event stage | `act45side_01` |
| `actXXmini_YY` | Mini-story event stage | `act10mini_01` |

#### Important Notes

- **`code` differs from stage_id**: `main_12-01` has code `"12-2"`, not `"12-1"`. Always use `code` for display, `stageId` for internal lookup.
- **Hard mode stages (`#f#`)** should be filtered out when building story order — they reference both the normal stage and a gating stage (e.g., `main_02-08`), creating false dependency chains.
- **Dependencies can reference stages outside the current chapter** (tutorial stages, previous chapter stages, sub-stages). These become "in-degree 0" nodes in topological sort when processing chapters in isolation.

---

### activity_table.json

Defines events/activities.

**Root structure**: `{ "basicInfo": { "<activity_id>": { ... }, ... } }`

#### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique activity ID | `"act10d5"`, `"act45side"` |
| `type` | string | Internal game type | `"TYPE_ACT9D0"`, `"MINISTORY"` |
| `displayType` | string | Display category | `"SIDESTORY"`, `"MINISTORY"`, `"BRANCHLINE"` |
| `name` | string | Event name (Japanese) | `"ウルサスの子供たち"` |
| `startTime` | int | Unix timestamp (start) | `1770688800` |
| `endTime` | int | Unix timestamp (end) | `1771873199` |
| `hasStage` | bool | Has playable stages | `true` |
| `isReplicate` | bool | Rerun of past event | `false` |

#### Activity Types (story-relevant)

| displayType | Description |
|-------------|-------------|
| `SIDESTORY` | Full side story event |
| `MINISTORY` | Mini/short side story event |
| `BRANCHLINE` | Branch story event |
| `NONE` | Gameplay-only or special event |

---

## Story JSON Files

### File Naming Conventions

Located in `gamedata/story/obt/main/` (main story) and `gamedata/story/activities/<event_id>/` (events).

| Pattern | Type | Description |
|---------|------|-------------|
| `level_main_XX-YY_beg.json` | Pre-battle | Story before battle stage XX-YY |
| `level_main_XX-YY_end.json` | Post-battle | Story after battle stage XX-YY |
| `level_main_XX-YY_end_variationNN.json` | Branch | Alternative ending (branching story) |
| `level_st_XX-YY.json` | Interlude | Side/interlude story |
| `level_spst_XX-YY.json` | Special interlude | Extra special story |
| `level_<event_id>_stNN.json` | Event story | Event story file |
| `level_<event_id>_NN.json` | Event stage | Event stage story |

### Story JSON Structure

```json
{
    "lang": "ja_JP",
    "eventid": "main_0",
    "eventName": "暗黒時代・上",
    "entryType": "MAINLINE",
    "storyCode": "0-1",
    "avgTag": "戦闘前",
    "storyName": "崩落",
    "storyInfo": "レユニオンが起こした暴動によって...",
    "storyList": [ ... ],
    "OPTIONTRACE": false
}
```

#### Root Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `lang` | string | Language code | `"ja_JP"` |
| `eventid` | string | Parent event/zone ID | `"main_0"`, `"act10d5"` |
| `eventName` | string | Event display name | Japanese text |
| `entryType` | string | Story category | `"MAINLINE"`, `"ACTIVITY"`, `"MINI_ACTIVITY"` |
| `storyCode` | string | Stage display code | `"0-1"`, `""` (empty for some events) |
| `avgTag` | string | Story phase label | `"戦闘前"`, `"戦闘後"`, `"幕間"` |
| `storyName` | string | Story title | Japanese text |
| `storyInfo` | string | Plot summary | Japanese text |
| `storyList` | array | Dialogue/narrative elements | See below |
| `OPTIONTRACE` | bool | Has player choice branches | `true`, `false` |

#### storyList Element Types

Each element has `id` (int), `prop` (string), and `attributes` (object).

| prop | Description | Key attributes |
|------|-------------|----------------|
| `HEADER` | Story header/title card | `key`, `is_skippable`, `fit_mode` |
| `Dialog` | Dialog section marker | (empty) |
| `Character` | Character appearance | `name` (e.g., `"char_002_amiya_1#5"`) |
| `name` | Dialogue/narration line | `content` (text), `name` (speaker, optional) |
| `PlayMusic` | Background music | `key`, `intro`, `volume`, `crossfade` |
| `StopMusic` | Stop music | `fadetime` |
| `Background` | Background image | `image`, `x`, `y`, `xScale`, `yScale`, `fadetime` |
| `Image` | Display image | `image`, `x`, `y`, `xScale`, `yScale` |
| `ImageTween` | Image animation | `xFrom`, `yFrom`, `xTo`, `yTo`, `duration` |
| `Blocker` | Fade/transition | `a`, `r`, `g`, `b`, `fadetime`, `block` |
| `Delay` | Pause | `time` |
| `CameraShake` | Camera shake effect | `duration`, `xstrength`, `ystrength` |
| `PlaySound` | Sound effect | `key`, `volume` |
| `Decision` | Player choice | `options` (`;`-separated), `values` (`;`-separated) |
| `Predicate` | End of choice branch | `references` (`;`-separated) |

#### Notes on storyList

- **Dialogue lines** (`prop: "name"`): If `attributes.name` is present, it's a character speaking. If absent, it's narration.
- **Character models**: Format `char_XXX_name_N#M` where `N#M` is the appearance variant (emotion/pose).
- **Player choices** (`Decision`/`Predicate`): Used together — `Decision` shows options, content between `Decision` and `Predicate` with matching references forms the branch.

---

## Auxiliary Data Files

### chardict.json

Character code name to display name mapping.

```json
{
    "amiya": {"name": "アーミヤ", "id": "002"},
    "chen": {"name": "チェン", "id": "010"}
}
```

### charinfo.json

Detailed character profiles with story entries.

```json
{
    "char_002_amiya": {
        "charID": "char_002_amiya",
        "storyTextAudio": [
            {
                "storyTitle": "基礎情報",
                "stories": [
                    {
                        "storyText": "...",
                        "unLockType": "DIRECT",
                        "unLockParam": ""
                    }
                ]
            }
        ]
    }
}
```

### storyinfo.json

Story path to summary text mapping, useful for previews.

```json
{
    "obt/main/level_main_00-01_beg": "レユニオンが起こした暴動によって...",
    "activities/a001/level_a001_01_beg": "財宝の伝説に揺れる滴水村は..."
}
```

### wordcount.json

Word count per story, used for story ordering in events.

### extrastory.json

Hidden/extra stories not linked from normal stage progression.

```json
{
    "extra": [
        {"storyName": "逆行", "storyTxt": "activities/act13side/level_act13side_hidden_st01"}
    ]
}
```

---

## Data Relationships

```
zone_table.json (zones/chapters)
    │
    ├── zoneId referenced by stage_table stages
    │
    ├── MAINLINE zones: main_0 ~ main_14
    │   └── chapter number = zone_id suffix (main_N -> N)
    │
    └── MAINLINE_ACTIVITY zones: act*mainss_zone*
        └── chapter number = zoneNameTitleCurrent (15, 16, ...)

stage_table.json (stages within zones)
    │
    ├── stageId -> levelId -> story file path
    │   e.g., main_00-01 -> Obt/Main/level_main_00-01
    │        -> level_main_00-01_beg.json + level_main_00-01_end.json
    │
    ├── unlockCondition -> dependency graph for ordering
    │
    └── code -> display stage number (may differ from stage_id numbering)

activity_table.json (events)
    │
    ├── id matches story file directory name
    │   e.g., act10d5 -> gamedata/story/activities/act10d5/
    │
    └── type/displayType determines processing logic

story JSON files (narrative content)
    └── storyList contains dialogue, effects, choices
```

## Special Cases and Gotchas

1. **Chapter numbering mismatch**: `stage_id` numbers don't always match `code` display numbers. Example: `main_12-01` has code `"12-2"`, and `st_12-01` has code `"12-1"`.

2. **MINISTORY events**: Have separate gameplay stages (in stage_table) and story stages (level_*_st*.json files). Only story stages should be processed.

3. **Branching stories (Chapter 15+)**: `OPTIONTRACE: true` indicates player choices affect the story. Variation files (`_variation01`, `_variation02`) provide alternative endings.

4. **Hard mode stages (`#f#`)**: Create false dependencies in the stage graph (depend on both the normal stage AND a gating stage). Must be excluded from story ordering.

5. **External dependencies in topological sort**: Main story stages often depend on tutorial (`tr_XX`), sub (`sub_XX-YY`), or previous chapter stages that are outside the current chapter's scope. These become in-degree 0 nodes and need natural sort tiebreaking.

6. **Event ID patterns**:
   - `actNNd0/d5` = Major event (TYPE_ACT3D0, TYPE_ACT4D0, etc.)
   - `actNNside` = Side story event
   - `actNNmini` = Mini story event
   - `actNmainss` = Main story supplement
