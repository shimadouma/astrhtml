#!/usr/bin/env python3
"""Extract an event's stories as a single readable Markdown transcript.

This produces the input a language model reads when generating AI commentary
for an event. Output goes to build/ai_input/{event_id}.md, which is a
regenerable intermediate and is not committed.

Usage:
    uv run python scripts/extract_story_text.py act45side
    uv run python scripts/extract_story_text.py act45side --stdout
"""
import argparse
import sys
from pathlib import Path

# Allow running as a script from the repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import AI_INPUT_PATH, ARKNIGHTS_STORY_JSON_PATH
from src.lib.commentary_paths import build_stage_ref_map
from src.lib.event_parser import get_events_with_stories
from src.lib.story_parser import parse_event_stories
from src.lib.story_text import extract_transcript, strip_markup


def find_event(event_id: str):
    """Locate an event by ID, including replicate events.

    Args:
        event_id: Event ID (e.g. 'act45side')

    Returns:
        Event object, or None if not found
    """
    events = get_events_with_stories(ARKNIGHTS_STORY_JSON_PATH)
    for event in events:
        if event.event_id == event_id:
            return event
    return None


def build_markdown(event) -> str:
    """Render an event's stories as a Markdown transcript.

    Stories appear in game order, each headed by its stage code so that the
    commentary's stage_refs can cite them.

    Args:
        event: Event object with parsed stories

    Returns:
        Markdown document as a string
    """
    stage_refs = build_stage_ref_map(event)

    lines = [
        f"# {event.event_name}",
        "",
        f"- イベントID: `{event.event_id}`",
        f"- 種別: {event.activity_info.display_type_label}",
        f"- ストーリー数: {len(stage_refs)}",
        "",
        "このファイルは AI 解説生成用に自動抽出されたものです。",
        "各セクションの見出しにある `stage_ref` を解説の `stage_refs` に使用してください。",
        "",
        "---",
        "",
    ]

    # Some events ship identical text in a stage's pre-battle and post-battle
    # files. Emitting both would double the reading cost for no added content,
    # so identical transcripts under the same stage_ref are collapsed.
    seen_transcripts = {}

    for entry in stage_refs:
        story = entry['story']
        heading = entry['stage_code'] or entry['page_name']
        title = strip_markup(story.story_name or '')
        # Combat stages split into pre-battle and post-battle story files that
        # share one page, so the phase belongs in the heading to tell them apart.
        phase = entry['story_phase']
        suffix = f"（{phase}）" if phase else ""

        transcript = extract_transcript(story)
        fingerprint = (entry['stage_ref'], "\n".join(transcript))
        if fingerprint in seen_transcripts:
            lines.append(
                f"## {heading} {title}{suffix}".rstrip()
                + f" — 本文は{seen_transcripts[fingerprint]}と同一のため省略"
            )
            lines.append("")
            continue
        seen_transcripts[fingerprint] = f"「{heading}（{phase}）」" if phase else f"「{heading}」"

        lines.append(f"## {heading} {title}{suffix}".rstrip())
        lines.append("")
        lines.append(f"- stage_ref: `{entry['stage_ref']}`")
        lines.append("")

        story_info = strip_markup(story.story_info or '')
        if story_info:
            lines.append(f"**あらすじ(公式)**: {story_info}")
            lines.append("")

        if transcript:
            lines.extend(transcript)
        else:
            lines.append("（本文なし）")
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description='Extract event stories as a Markdown transcript for AI commentary'
    )
    parser.add_argument('event_id', help='Event ID (e.g. act45side)')
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Write to stdout instead of build/ai_input/{event_id}.md'
    )
    args = parser.parse_args()

    event = find_event(args.event_id)
    if not event:
        print(f"Error: event '{args.event_id}' not found or has no stories", file=sys.stderr)
        return 1

    parse_event_stories(event)
    if not event.stories:
        print(f"Error: event '{args.event_id}' has no parsable stories", file=sys.stderr)
        return 1

    markdown = build_markdown(event)

    if args.stdout:
        sys.stdout.write(markdown)
        return 0

    AI_INPUT_PATH.mkdir(parents=True, exist_ok=True)
    output_path = AI_INPUT_PATH / f"{args.event_id}.md"
    output_path.write_text(markdown, encoding='utf-8')

    print(f"Extracted {len(event.stories)} stories ({len(markdown):,} chars)")
    print(f"Output: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
