---
name: ai-commentary
description: Generate the AI commentary (AI解説) page data for an Arknights event story — a retrospective summary, revealed facts, open plot threads, and a glossary. Use when asked to create, write, or regenerate commentary/解説 for an event ID such as act45side.
argument-hint: "[event_id]"
arguments: [event_id]
allowed-tools: Read, Write, Bash(uv run python scripts/extract_story_text.py:*), Bash(uv run python scripts/validate_commentary.py:*), Bash(uv run python build.py:*)
---

# AI Commentary Generation

Generate `content/commentary/$event_id.json` for the Arknights event `$event_id`.

The output is **data, not HTML** — the build renders it. Never write HTML here.

## Procedure

### 1. Extract the story text

```bash
uv run python scripts/extract_story_text.py $event_id
```

This writes `build/ai_input/$event_id.md`. If the event ID is not found, stop and
report it — do not guess a different ID.

### 2. Read the whole transcript

Read `build/ai_input/$event_id.md` **in full**. Large events run past a single
Read call's limit; continue with `offset`/`limit` until you reach the end. Do not
summarize from a partial read — a commentary built on half the story is worse
than none.

Note while reading:
- Each `## ` heading gives a `stage_ref` you must cite from.
- Combat stages appear twice, as （戦闘前） and （戦闘後）, sharing one
  `stage_ref`. That is expected.
- `**あらすじ(公式)**` lines are the official per-stage blurbs — useful anchors,
  but write your own prose rather than copying them.

### 3. Write the JSON

Write `content/commentary/$event_id.json` following @reference/schema.md.

### 4. Validate

```bash
uv run python scripts/validate_commentary.py --event $event_id
```

Fix every error and re-run until it passes. The most common failure is an
invented `stage_ref` — only refs present in the transcript are valid.

### 5. Render and report

```bash
uv run python build.py --event $event_id --no-check-links
```

Then tell the user the file was written, how many entries per section, and that
`dist/events/$event_id/commentary.html` is viewable via `uv run python preview.py`.

## Content requirements

The purpose is **retrospective clarification**. Arknights scenarios rely on
indirect, allusive phrasing; a reader who has finished the story and is unsure
what actually happened should leave this page certain. Resolve the indirection
into plain statements.

Write all content in **Japanese** (JSON keys stay English).

- **summary** — chronological blocks covering the whole event, not just the
  opening. State plainly who did what and why. Where the text is deliberately
  oblique, say what it means in plain terms. 4–8 blocks suits most events.
- **revealed_facts** — what this event establishes. Set `basis` to `stated` only
  when the text says it outright; use `implied` when you are inferring from
  context. This distinction is the point of the field — do not default
  everything to `stated`.
- **open_threads** — questions the event raises and does not answer, each with
  the scene that raised it in `context`. Omit the section rather than padding it
  with invented mysteries.
- **glossary** — terms, organizations, locations, and concepts a reader might not
  retain. Define them from *this event's* usage. Add `reading` only for terms
  whose pronunciation is genuinely non-obvious.

### Grounding rules

These are absolute:

1. **Every claim must come from the transcript.** No outside lore, no other
   events, no fan interpretation, no speculation about future story.
2. **Every entry carries `stage_refs`** pointing at the stage(s) that support it.
   An entry you cannot attribute to a stage does not belong in the file.
3. **Uncertainty is stated, not hidden.** If the story leaves something
   ambiguous, present it as ambiguous — in `open_threads`, or as an `implied`
   fact — instead of resolving it yourself.
4. **No invented proper nouns.** Names, ranks, and place names must appear in the
   transcript.

## Regenerating

If `content/commentary/$event_id.json` already exists, tell the user it exists
and ask whether to overwrite before proceeding.

## One event per run

Generate commentary for the single event given in `$event_id` only. If asked to
backfill several events, do them one at a time and stop after each so the output
can be reviewed — the diff review is the quality gate, and batching defeats it.
`scripts/list_missing_commentary.py` shows what remains; see
`docs/ai_commentary_workflow.md` for the backfill procedure.
