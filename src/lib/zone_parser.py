"""Zone table parser for main story chapters."""
from typing import Dict, List, Optional
from pathlib import Path
import json

from .data_loader import load_json
from ..models.zone_info import ZoneInfo


def load_zone_table(data_path: Path) -> Dict[str, ZoneInfo]:
    """Load zone_table.json and return dictionary of ZoneInfo objects"""
    zone_table_path = data_path / "gamedata" / "excel" / "zone_table.json"
    data = load_json(zone_table_path)
    if not data:
        return {}
    
    zones = {}
    zones_data = data.get('zones', {})
    
    for zone_id, zone_data in zones_data.items():
        # Only process main story zones
        if not zone_id.startswith('main_') or not zone_data.get('type') == 'MAINLINE':
            continue
        
        # Check if story files exist for this chapter
        chapter_number = zone_data.get('zoneIndex', 0)
        story_dir = data_path / "gamedata" / "story" / "obt" / "main"
        chapter_pattern = f"level_main_{chapter_number:02d}-*"
        has_stories = len(list(story_dir.glob(chapter_pattern))) > 0 if story_dir.exists() else False
        
        # Override canPreview if we have story files
        can_preview = zone_data.get('canPreview', False) or has_stories
            
        zones[zone_id] = ZoneInfo(
            zone_id=zone_id,
            zone_index=zone_data.get('zoneIndex', 0),
            zone_type=zone_data.get('type', ''),
            zone_name_first=zone_data.get('zoneNameFirst', ''),
            zone_name_second=zone_data.get('zoneNameSecond', ''),
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