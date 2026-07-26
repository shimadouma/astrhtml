#!/usr/bin/env python3
"""Validate committed AI commentary files.

Checks that every content/commentary/*.json file is well-formed, matches its
filename, and cites only stage refs that resolve to real story pages. Run in
CI so a malformed hand-edit cannot reach the site.

Usage:
    uv run python scripts/validate_commentary.py
    uv run python scripts/validate_commentary.py --event act45side
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ARKNIGHTS_STORY_JSON_PATH, COMMENTARY_PATH
from src.lib.commentary_parser import SCHEMA_VERSION, SECTION_LABELS, Commentary
from src.lib.commentary_paths import build_stage_ref_map
from src.lib.event_parser import get_events_with_stories
from src.lib.story_parser import parse_event_stories

VALID_BASIS = {'stated', 'implied'}


def load_known_stage_refs(event_ids: Set[str]) -> Dict[str, Set[str]]:
    """Resolve the set of valid stage refs for each requested event.

    Args:
        event_ids: Event IDs to resolve

    Returns:
        Mapping of event_id to its set of valid stage refs. Events that do not
        exist in the story data are absent from the mapping.
    """
    known: Dict[str, Set[str]] = {}
    events = get_events_with_stories(ARKNIGHTS_STORY_JSON_PATH)

    for event in events:
        if event.event_id not in event_ids:
            continue
        parse_event_stories(event)
        entries = build_stage_ref_map(event)
        known[event.event_id] = {e['stage_ref'] for e in entries}

    return known


def validate_file(path: Path, known_refs: Dict[str, Set[str]]) -> List[str]:
    """Validate a single commentary file.

    Args:
        path: Path to the commentary JSON file
        known_refs: Mapping of event_id to valid stage refs

    Returns:
        List of human-readable error messages (empty if valid)
    """
    errors: List[str] = []
    expected_event_id = path.stem

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    except OSError as e:
        return [f"could not read file: {e}"]

    if not isinstance(data, dict):
        return ["top level must be a JSON object"]

    # Identity and version
    if data.get('event_id') != expected_event_id:
        errors.append(
            f"event_id {data.get('event_id')!r} does not match filename "
            f"{expected_event_id!r}"
        )

    version = data.get('schema_version')
    if version is None:
        errors.append("missing required field 'schema_version'")
    elif version != SCHEMA_VERSION:
        errors.append(
            f"schema_version {version} is not supported "
            f"(renderer expects {SCHEMA_VERSION})"
        )

    commentary = Commentary.from_dict(data)
    if commentary.is_empty:
        errors.append("all content sections are empty")

    # Required text on each entry
    for i, item in enumerate(commentary.summary):
        if not item.body.strip():
            errors.append(f"summary[{i}]: 'body' is empty")
    for i, item in enumerate(commentary.revealed_facts):
        if not item.fact.strip():
            errors.append(f"revealed_facts[{i}]: 'fact' is empty")
        if item.basis not in VALID_BASIS:
            errors.append(
                f"revealed_facts[{i}]: basis {item.basis!r} must be one of "
                f"{sorted(VALID_BASIS)}"
            )
    for i, item in enumerate(commentary.open_threads):
        if not item.thread.strip():
            errors.append(f"open_threads[{i}]: 'thread' is empty")
    for i, item in enumerate(commentary.glossary):
        if not item.term.strip():
            errors.append(f"glossary[{i}]: 'term' is empty")
        if not item.definition.strip():
            errors.append(f"glossary[{i}]: 'definition' is empty")

    # Stage refs must resolve to real story pages
    valid = known_refs.get(expected_event_id)
    if valid is None:
        errors.append(
            f"event {expected_event_id!r} not found in story data "
            "(cannot verify stage_refs)"
        )
    else:
        for section_name in SECTION_LABELS:
            for i, item in enumerate(getattr(commentary, section_name)):
                for ref in item.stage_refs:
                    if ref not in valid:
                        errors.append(
                            f"{section_name}[{i}]: unknown stage_ref {ref!r}"
                        )

    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate AI commentary files')
    parser.add_argument('--event', help='Validate only this event ID')
    parser.add_argument(
        '--commentary-dir',
        default=str(COMMENTARY_PATH),
        help='Directory holding commentary JSON files'
    )
    args = parser.parse_args()

    commentary_dir = Path(args.commentary_dir)
    if not commentary_dir.exists():
        print(f"No commentary directory at {commentary_dir}; nothing to validate.")
        return 0

    if args.event:
        files = [commentary_dir / f"{args.event}.json"]
        if not files[0].exists():
            print(f"Error: no commentary file for event '{args.event}'", file=sys.stderr)
            return 1
    else:
        files = sorted(commentary_dir.glob('*.json'))

    if not files:
        print(f"No commentary files found in {commentary_dir}; nothing to validate.")
        return 0

    print(f"Validating {len(files)} commentary file(s)...")
    known_refs = load_known_stage_refs({p.stem for p in files})

    total_errors = 0
    for path in files:
        errors = validate_file(path, known_refs)
        if errors:
            total_errors += len(errors)
            print(f"\n❌ {path.name}")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✅ {path.name}")

    if total_errors:
        print(f"\nValidation failed with {total_errors} error(s).")
        return 1

    print(f"\nAll {len(files)} commentary file(s) valid.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
