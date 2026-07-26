# AI Commentary Workflow

Operator guide for generating the "AI解説" page for an event story.

## What this produces

For an event, a single page at `dist/events/{event_id}/commentary.html` containing:

- **あらすじ** — a chronological retelling that resolves the story's indirect phrasing
- **判明した事実** — what the event establishes, marked as stated or implied
- **伏線・未回収の謎** — questions raised and left unanswered
- **用語集** — terms, organizations, and concepts defined from this event's usage

Every entry links to the story pages that support it.

The event page gets an "AI解説" entry as the last item in its story list.

## Why generation is manual

Story text is large (100KB–600KB of transcript per event) and commentary quality
depends on reading the whole thing with judgment. Running that in CI on every build
would be slow, expensive, and non-deterministic. Instead:

- **You** generate the data locally, once per event, and review it
- **CI** only renders committed data to HTML

Because the committed artifact is JSON rather than HTML, changing the template or
stylesheet never means regenerating anything.

## Prerequisites

```bash
uv sync
git submodule update --init --recursive
```

Confirm the event exists in the submodule data. If the event is newer than the
pinned submodule commit, update it first:

```bash
git submodule update --remote --merge
```

## Procedure

### 1. Check whether the event needs commentary

```bash
uv run python scripts/list_missing_commentary.py
```

Events are listed newest first. Pick one.

### 2. Run the skill

```
/ai-commentary act49side
```

The skill extracts the transcript, reads it in full, and writes
`content/commentary/act49side.json`. Large events take a while — it must read the
whole story, not skim it.

If the file already exists, the skill asks before overwriting.

### 3. Review the diff

This is the step that matters most. Read the generated JSON as prose:

```bash
git diff --no-index /dev/null content/commentary/act49side.json
```

Check for:

- **Fabrication** — every claim should be traceable to the cited stages. If you
  don't recognize a plot point, verify it against `build/ai_input/act49side.md`.
- **`basis` accuracy** — `stated` means the text says it outright; `implied` means
  it is an inference. Everything marked `stated` is a claim you are publishing as
  fact.
- **Invented proper nouns** — names and places must appear in the source.
- **Completeness** — does the summary cover the ending, or does it trail off
  partway through?

Edit the JSON directly if something is wrong. Hand edits are expected and safe;
validation will catch structural mistakes.

### 4. Validate

```bash
uv run python scripts/validate_commentary.py --event act49side
```

This checks the schema, that `event_id` matches the filename, that `basis` values
are legal, and that every `stage_refs` entry corresponds to a real story page.
The most common failure is an invented stage code.

### 5. Render and review in a browser

```bash
uv run python build.py --event act49side
uv run python preview.py
```

Open `http://localhost:8000/events/act49side/`. Confirm the "AI解説" link appears
at the end of the story list, and that stage-ref chips on the commentary page link
to the right scenes.

### 6. Commit

```bash
git add content/commentary/act49side.json
git commit -m "Add AI commentary for act49side"
```

Commit only the JSON. `build/ai_input/` is gitignored and should never appear in
the diff.

## Backfilling the remaining events

As of the initial release only `act49side` has commentary. The rest are a backlog
to work through incrementally.

### Check the backlog

```bash
# Events still needing commentary, newest first
uv run python scripts/list_missing_commentary.py

# How many are left
uv run python scripts/list_missing_commentary.py | head -1

# Just the next few to work on
uv run python scripts/list_missing_commentary.py --limit 5
```

The script also warns if `content/commentary/` holds a file for an event ID that no
longer exists in the story data, which happens if an event is renamed upstream.

### Suggested order

Work newest-first (the default listing order). Recent events are the ones readers
are most likely to be looking up, and they benefit most from a retrospective while
the story is still being discussed.

Two exceptions worth pulling forward:

- **Events that continue an ongoing arc.** A reader finishing a new event often
  wants the previous installment summarized too.
- **Events with heavy lore.** Long SIDESTORY events with dense terminology gain
  more from a glossary than short MINISTORY ones.

### One event at a time

**Do not batch.** Generate, review, and commit one event per run:

```bash
/ai-commentary act48side
# review the diff, validate, then commit
```

The reason is that the review step in section 3 is the quality gate, and it does not
scale — reviewing five events' commentary at once means skimming all five. A
commentary that reads plausibly but misstates the plot is worse than no commentary,
because readers trust it. One event per commit also keeps `git log` useful and makes
a bad entry easy to revert in isolation.

Budget roughly one session per event. Large events (200KB+ of transcript) take
longer because the whole story has to be read.

### Verify the batch periodically

After adding several events, validate everything at once and do a full build:

```bash
uv run python scripts/validate_commentary.py     # validates every committed file
uv run python build.py                           # full build with link checking
uv run python scripts/list_missing_commentary.py --covered
```

Watch the build output for `Warning: ... stage_refs did not resolve` — if a whole
event's refs stop resolving after a submodule update, the page-name mapping changed
upstream rather than the commentary being wrong. See the note on the three-way
filename duplication in `CLAUDE.md`.

### Main story chapters

Not supported yet. Main story uses a separate generator path
(`MainStoryGenerator`, `main/chapter_NN/`); support would be added via
`content/commentary/main_XX.json`. Do not try to run the skill against a
`main_XX` ID — the extractor only resolves event IDs.

## Troubleshooting

**"event not found or has no stories"**
The event ID does not exist in the current submodule data. Check the spelling
against `data/ArknightsStoryJson/ja_JP/gamedata/story/activities/`, and update the
submodule if the event is recent.

**"unknown stage_ref 'XX-9'"**
The commentary cites a stage that has no story page. Valid refs are listed in
`build/ai_input/{event_id}.md` under each `## ` heading. Fix or remove the ref.

**The commentary link does not appear on the event page**
The JSON is missing, unparsable, or has all sections empty. Run the validator; also
confirm the filename stem exactly matches the event ID.

**Stage-ref chips render as plain text instead of links**
That ref did not resolve to a page. This is deliberate degradation so the build
does not break — run the validator to find it.

**Duplicate 戦闘前/戦闘後 sections in the transcript**
Expected. Combat stages have separate pre- and post-battle story files sharing one
page. When the two files are byte-identical, the extractor collapses the second one
and notes the omission.

## Scope

Events only for now. Main story chapters use a separate generator path and are a
planned extension.
