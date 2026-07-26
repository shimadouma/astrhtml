# Commentary JSON schema (schema_version 1)

Written to `content/commentary/{event_id}.json`. Validated by
`scripts/validate_commentary.py`; rendered by `src/generators/commentary_generator.py`.

## Full shape

```json
{
  "schema_version": 1,
  "event_id": "act45side",
  "event_name": "安らかな譫言",
  "generated_at": "2026-07-26",
  "generator": "claude-opus-5",
  "summary": [
    {
      "heading": "夢の城への招待",
      "body": "祥子は不思議な夢から目を覚まし、ヴィグナにその内容を打ち明ける。……",
      "stage_refs": ["SS-ST-1", "SS-1"]
    }
  ],
  "revealed_facts": [
    {
      "fact": "アイリスは文通相手を救うために夢の城の力を使っていた。",
      "basis": "stated",
      "stage_refs": ["SS-ST-1"]
    },
    {
      "fact": "夢の城の維持には見る者の記憶が消費されている可能性がある。",
      "basis": "implied",
      "stage_refs": ["SS-6"]
    }
  ],
  "open_threads": [
    {
      "thread": "夢の城を最初に作った人物が誰なのかは明かされない。",
      "context": "ベナが「あの方」と呼ぶ相手について、アイリスは答えを避けた。",
      "stage_refs": ["SS-8"]
    }
  ],
  "glossary": [
    {
      "term": "夢の城",
      "reading": "ゆめのしろ",
      "definition": "アイリスとベナが管理する、訪れた者に望んだ夢を見せる領域。……",
      "stage_refs": ["SS-ST-1", "SS-4"]
    }
  ]
}
```

## Field reference

### Top level

| Field | Required | Notes |
|---|---|---|
| `schema_version` | yes | Must be `1`. |
| `event_id` | yes | Must equal the filename stem. |
| `event_name` | recommended | The event's Japanese name, from the transcript header. |
| `generated_at` | recommended | `YYYY-MM-DD`. Use today's date. |
| `generator` | recommended | Model identifier, e.g. `claude-opus-5`. |

At least one content section must be non-empty. Omit a section entirely (or use
`[]`) when there is nothing to say — the page skips empty sections.

### `summary[]`

| Field | Required | Notes |
|---|---|---|
| `heading` | recommended | Short phase label. Rendered as a subheading. |
| `body` | **yes** | Plain prose. Plain text only — no Markdown, no HTML. |
| `stage_refs` | yes | Stages this block covers. |

### `revealed_facts[]`

| Field | Required | Notes |
|---|---|---|
| `fact` | **yes** | One fact per entry. |
| `basis` | **yes** | Exactly `stated` or `implied`. Any other value fails validation. |
| `stage_refs` | yes | Stages establishing the fact. |

### `open_threads[]`

| Field | Required | Notes |
|---|---|---|
| `thread` | **yes** | The unresolved question. |
| `context` | optional | The scene that raised it. |
| `stage_refs` | yes | Stages where the thread appears. |

### `glossary[]`

| Field | Required | Notes |
|---|---|---|
| `term` | **yes** | The term as written in the story. |
| `definition` | **yes** | Grounded in this event's usage. |
| `reading` | optional | Kana reading; include only when non-obvious. |
| `stage_refs` | yes | Stages where the term appears. |

## stage_refs rules

- Values must exactly match a `stage_ref` from `build/ai_input/{event_id}.md`
  (e.g. `SS-1`, `SS-ST-1`). Validation rejects anything else.
- Combat stages have one `stage_ref` shared by their 戦闘前/戦闘後 halves.
- Order refs as they occur in the story.
- Prefer 1–3 refs per entry; cite the stages that actually support the claim
  rather than every stage the subject is mentioned in.

## Text conventions

- Japanese prose. Full-width punctuation (`。` `、`).
- Plain text only. The renderer escapes HTML, so tags would appear literally.
- No `\n` inside a `body` — split into separate `summary` blocks instead.
- Do not include the event name in every heading; the page is already titled.
