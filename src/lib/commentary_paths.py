"""Mapping between an event's stories and their generated page names.

Both the AI commentary input extractor and the commentary renderer need to
agree on which stage_ref identifies which story page. This module is the
single source of that mapping so a stage_ref written by the model always
resolves to a real `stories/{page_name}.html` file.

The page-name rules mirror those in generators/event_generator.py, which
determines the actual output filenames.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import ARKNIGHTS_STORY_JSON_PATH
from ..lib.event_parser import get_ordered_stories_for_event
from ..models.event import Event

# Event types whose story_code is empty, requiring filename-based matching
_FILENAME_MATCHED_TYPES = ('MINISTORY', 'TYPE_ACT4D0')


def build_stage_ref_map(event: Event) -> List[Dict[str, Any]]:
    """Build the ordered list of stage references for an event.

    Args:
        event: Event object with parsed stories

    Returns:
        List of dicts in game order, each containing:
            stage_ref: Identifier the model should cite (stage code or page name)
            page_name: Basename of the generated HTML page (no extension)
            stage_code: Stage code from stage_table, may be empty
            story_phase: '戦闘前' / '戦闘後' / '間章', may be empty
            story: The Story object
    """
    ordered = get_ordered_stories_for_event(event.event_id, ARKNIGHTS_STORY_JSON_PATH)
    event_type = event.activity_info.type

    entries = []
    for file_name, stage_info in ordered:
        story = _match_story(event, file_name, stage_info, event_type)
        if not story:
            # Stages without story content have no page to cite
            continue

        page_name = _resolve_page_name(event, story, file_name, stage_info, event_type)
        if not page_name:
            continue

        stage_code = stage_info.get('code', '')
        entries.append({
            'stage_ref': stage_code or page_name,
            'page_name': page_name,
            'stage_code': stage_code,
            'story_phase': stage_info.get('story_phase', ''),
            'story': story,
        })

    return entries


def _match_story(event: Event, file_name: str, stage_info: Dict[str, str],
                 event_type: Optional[str]):
    """Find the Story object corresponding to an ordered story file entry."""
    if event_type in _FILENAME_MATCHED_TYPES:
        return _match_by_filename(event, file_name)

    # Match by stage code first
    stage_code = stage_info.get('code', '')
    if stage_code:
        for story in event.stories:
            if story.story_code == stage_code:
                return story

    # Hidden stories have no matching stage code; fall back to the filename
    return _match_by_filename(event, file_name)


def _match_by_filename(event: Event, file_name: str):
    """Find a Story by the basename of its source JSON file.

    Stories are parsed in story_files order, so the index of the matching
    file is the index of the story.
    """
    target = Path(file_name).name
    for index, story_file in enumerate(event.story_files):
        if story_file.name == target:
            if index < len(event.stories):
                return event.stories[index]
            return None
    return None


def _resolve_page_name(event: Event, story, file_name: str,
                       stage_info: Dict[str, str], event_type: Optional[str]) -> str:
    """Determine the generated HTML basename for a story.

    Mirrors the filename logic in EventGenerator.generate().
    """
    if event_type == 'MINISTORY':
        return stage_info.get('code', '') or Path(file_name).stem

    if event_type == 'TYPE_ACT4D0':
        target = Path(file_name).name
        for index, story_file in enumerate(event.story_files):
            if story_file.name == target:
                return f"story_{index}"
        return ''

    if story.story_code and story.story_code.startswith('story_'):
        return story.story_code

    return story.story_code or stage_info.get('code', '') or Path(file_name).stem
