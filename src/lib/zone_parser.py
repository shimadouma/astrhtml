"""Zone table parser for main story chapters."""
from typing import Dict, List, Optional
from pathlib import Path
import json

from .data_loader import load_json
from ..models.zone_info import ZoneInfo


def _chapter_to_kanji(num: int) -> str:
    """Convert chapter number to Japanese kanji numeral (e.g. 15 -> '十五')"""
    if num == 0:
        return ''
    kanji_digits = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if num < 10:
        return kanji_digits[num]
    elif num < 20:
        return '十' + (kanji_digits[num % 10] if num % 10 else '')
    elif num < 100:
        return kanji_digits[num // 10] + '十' + (kanji_digits[num % 10] if num % 10 else '')
    return str(num)


def load_zone_table(data_path: Path) -> Dict[str, ZoneInfo]:
    """Load zone_table.json and return dictionary of ZoneInfo objects"""
    zone_table_path = data_path / "gamedata" / "excel" / "zone_table.json"
    data = load_json(zone_table_path)
    if not data:
        return {}
    
    zones = {}
    zones_data = data.get('zones', {})
    
    for zone_id, zone_data in zones_data.items():
        zone_type = zone_data.get('type', '')

        # Process standard MAINLINE zones (main_0 ~ main_14)
        # and MAINLINE_ACTIVITY zones (act*mainss_zone* for ch15+)
        if zone_id.startswith('main_') and zone_type == 'MAINLINE':
            # Chapter number from zone_id (e.g. main_9 -> 9)
            try:
                chapter_number = int(zone_id.replace('main_', ''))
            except (ValueError, TypeError):
                continue
        elif zone_type == 'MAINLINE_ACTIVITY':
            # Chapter number from zoneNameTitleCurrent (e.g. "15", "16")
            try:
                chapter_number = int(zone_data.get('zoneNameTitleCurrent', '0'))
            except (ValueError, TypeError):
                continue
        else:
            continue

        # Check if story files exist for this chapter
        story_dir = data_path / "gamedata" / "story" / "obt" / "main"
        chapter_pattern = f"level_main_{chapter_number:02d}-*"
        has_stories = len(list(story_dir.glob(chapter_pattern))) > 0 if story_dir.exists() else False

        # Override canPreview if we have story files
        can_preview = zone_data.get('canPreview', False) or has_stories

        # For MAINLINE_ACTIVITY zones, swap first/second names
        # (first is English title, second is Japanese title)
        if zone_type == 'MAINLINE_ACTIVITY':
            zone_name_first = f"第{_chapter_to_kanji(chapter_number)}章"
            zone_name_second = zone_data.get('zoneNameSecond', '')
        else:
            zone_name_first = zone_data.get('zoneNameFirst', '')
            zone_name_second = zone_data.get('zoneNameSecond', '')

        # Use main_N as canonical zone_id for consistent lookup
        canonical_zone_id = f"main_{chapter_number}"

        zones[canonical_zone_id] = ZoneInfo(
            zone_id=canonical_zone_id,
            zone_index=chapter_number,
            zone_type='MAINLINE',
            zone_name_first=zone_name_first,
            zone_name_second=zone_name_second,
            zone_name_title_current=zone_data.get('zoneNameTitleCurrent', ''),
            zone_name_title_ex=zone_data.get('zoneNameTitleEx', ''),
            zone_name_third=zone_data.get('zoneNameThird', ''),
            locked_text=zone_data.get('lockedText', ''),
            can_preview=can_preview
        )
    
    return zones


def get_available_main_chapters(zones: Dict[str, ZoneInfo]) -> List[int]:
    """Get list of available main story chapter numbers, sorted"""
    chapters = []
    for zone_info in zones.values():
        if zone_info.is_main_story():
            chapters.append(zone_info.chapter_number)
    
    return sorted(chapters)


def get_zone_by_chapter(zones: Dict[str, ZoneInfo], chapter: int) -> Optional[ZoneInfo]:
    """Get zone info for specific chapter number"""
    zone_id = f"main_{chapter}"
    return zones.get(zone_id)


def get_ordered_main_zones(zones: Dict[str, ZoneInfo]) -> List[ZoneInfo]:
    """Get main story zones ordered by chapter number"""
    main_zones = [zone for zone in zones.values() if zone.is_main_story()]
    return sorted(main_zones, key=lambda z: z.chapter_number)