"""AI commentary page generator."""
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base_generator import BaseGenerator
from ..config import DIST_PATH
from ..lib.commentary_parser import SECTION_LABELS, Commentary, load_commentary
from ..lib.commentary_paths import build_stage_ref_map
from ..models.event import Event
from ..utils.date_formatter import format_timestamp


class CommentaryGenerator(BaseGenerator):
    """Generator for AI commentary pages.

    Renders content/commentary/{event_id}.json to a single page per event.
    Events without a commentary file are skipped silently.
    """

    def generate(self, event: Event, output_path: Path = DIST_PATH) -> bool:
        """Generate the commentary page for an event.

        Args:
            event: Event object with parsed stories
            output_path: Output directory path

        Returns:
            True if a page was generated, False if the event has no commentary
        """
        commentary = load_commentary(event.event_id)
        if not commentary:
            return False

        # Resolve stage refs to story page links
        link_map = self._build_link_map(event)
        unresolved: Set[str] = set()

        event_dir = output_path / 'events' / event.event_id
        event_dir.mkdir(parents=True, exist_ok=True)
        commentary_path = event_dir / 'commentary.html'

        paths = self.get_relative_paths(commentary_path, output_path)

        context = {
            'event': {
                'event_id': event.event_id,
                'event_name': event.event_name,
                'activity_info': event.activity_info,
                'start_date': format_timestamp(event.activity_info.start_time),
                'end_date': format_timestamp(event.activity_info.end_time),
            },
            'commentary': commentary,
            'sections': self._build_sections(commentary),
            'section_label': SECTION_LABELS,
            'resolve_refs': lambda refs: self._resolve_refs(refs, link_map, unresolved),
            **paths
        }

        html = self.render_template('commentary.html', context)
        self.write_html_file(html, commentary_path)

        if unresolved:
            # A few bad refs mean a typo in hand-authored data; all of them mean
            # the stage_ref -> page mapping itself broke for this event.
            scope = "all" if not link_map else f"{len(unresolved)}"
            print(
                f"Warning: {scope} stage_refs did not resolve for {event.event_id} "
                f"({', '.join(sorted(unresolved))}); they render without links. "
                "Run scripts/validate_commentary.py to diagnose."
            )

        print(f"Generated commentary page: {commentary_path}")
        return True

    def _build_link_map(self, event: Event) -> Dict[str, str]:
        """Map each valid stage ref to its story page filename."""
        try:
            entries = build_stage_ref_map(event)
        except Exception as e:
            # A mapping failure should not break the build; refs just won't link.
            print(f"Warning: could not resolve stage refs for {event.event_id}: {e}")
            return {}
        return {e['stage_ref']: e['page_name'] for e in entries}

    def _resolve_refs(self, refs: List[str], link_map: Dict[str, str],
                      unresolved: Set[str]) -> List[Dict[str, Optional[str]]]:
        """Turn stage refs into label/href pairs for the template.

        Refs that do not resolve are rendered as plain labels rather than
        broken links, so stale data degrades instead of failing the build.
        Misses are collected in `unresolved` so the caller can report them.
        """
        resolved = []
        for ref in refs:
            page_name = link_map.get(ref)
            if not page_name:
                unresolved.add(ref)
            resolved.append({
                'label': ref,
                'href': f"stories/{page_name}.html" if page_name else None,
            })
        return resolved

    def _build_sections(self, commentary: Commentary) -> List[Dict[str, Any]]:
        """Build the list of non-empty sections in render order.

        Drives both the table of contents and each section's heading, so the
        two cannot disagree. SECTION_LABELS is the source of order and labels.
        """
        sections = []
        for key, label in SECTION_LABELS.items():
            items = getattr(commentary, key)
            if items:
                sections.append({'id': key, 'label': label, 'count': len(items)})
        return sections
