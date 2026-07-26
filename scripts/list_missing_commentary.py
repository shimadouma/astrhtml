#!/usr/bin/env python3
"""List events that have stories but no committed AI commentary.

Use this to see the commentary backlog and pick the next event to process.

Usage:
    uv run python scripts/list_missing_commentary.py
    uv run python scripts/list_missing_commentary.py --limit 10
    uv run python scripts/list_missing_commentary.py --covered
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ARKNIGHTS_STORY_JSON_PATH, INCLUDE_REPLICATE_EVENTS
from src.lib.commentary_parser import list_commentary_event_ids
from src.lib.event_parser import get_events_with_stories, sort_events_by_date
from src.utils.date_formatter import format_timestamp


def main():
    parser = argparse.ArgumentParser(
        description='List events lacking AI commentary'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Show only the first N events (newest first)'
    )
    parser.add_argument(
        '--covered',
        action='store_true',
        help='List events that already have commentary instead'
    )
    parser.add_argument(
        '--include-replicate',
        action='store_true',
        help='Include replicate (rerun) events, which the site excludes by default'
    )
    args = parser.parse_args()

    events = get_events_with_stories(ARKNIGHTS_STORY_JSON_PATH)

    if not (args.include_replicate or INCLUDE_REPLICATE_EVENTS):
        events = [e for e in events if not e.activity_info.is_replicate]

    events = sort_events_by_date(events, reverse=True)
    have_commentary = set(list_commentary_event_ids())

    if args.covered:
        selected = [e for e in events if e.event_id in have_commentary]
        heading = 'Events with commentary'
    else:
        selected = [e for e in events if e.event_id not in have_commentary]
        heading = 'Events without commentary'

    total = len(selected)
    if args.limit:
        selected = selected[:args.limit]

    print(f"{heading}: {total} of {len(events)} events")
    # Orphaned files indicate a renamed or removed event
    orphans = have_commentary - {e.event_id for e in events}
    if orphans:
        print(f"Warning: commentary exists for unknown events: {', '.join(sorted(orphans))}")
    print()

    if not selected:
        print("(none)")
        return 0

    for event in selected:
        start = format_timestamp(event.activity_info.start_time)
        label = event.activity_info.display_type_label
        print(f"  {event.event_id:16} {start:12} {label:12} {event.event_name}")

    if args.limit and total > args.limit:
        print(f"\n... and {total - args.limit} more")

    return 0


if __name__ == '__main__':
    sys.exit(main())
