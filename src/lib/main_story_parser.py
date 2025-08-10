"""Main story file parser and organizer."""
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import os
import re

from ..models.zone_info import ZoneInfo
from ..models.activity import ActivityInfo


class MainStoryFile:
    """Represents a main story file and its metadata"""
    
    def __init__(self, filename: str, file_path: Path):
        self.filename = filename
        self.file_path = file_path
        self.chapter = None
        self.stage_number = None
        self.stage_type = None  # 'beg', 'end', 'st', 'spst'
        self.stage_id = None
        
        self._parse_filename()
    
    def _parse_filename(self):
        """Parse filename to extract chapter, stage info"""
        base_name = self.filename.replace('level_', '').replace('.json', '')
        
        if base_name.startswith('main_'):
            # level_main_XX-YY_beg.json or level_main_XX-YY_end.json
            pattern = r'main_(\d+)-(\d+)_(beg|end)'
            match = re.match(pattern, base_name)
            if match:
                self.chapter = int(match.group(1))
                self.stage_number = int(match.group(2))
                self.stage_type = match.group(3)
                self.stage_id = f"main_{self.chapter:02d}-{self.stage_number:02d}"
        
        elif base_name.startswith('st_'):
            # level_st_XX-YY.json
            pattern = r'st_(\d+)-(\d+)'
            match = re.match(pattern, base_name)
            if match:
                self.chapter = int(match.group(1))
                self.stage_number = int(match.group(2))
                self.stage_type = 'st'
                self.stage_id = f"st_{self.chapter:02d}-{self.stage_number:02d}"
        
        elif base_name.startswith('spst_'):
            # level_spst_XX-YY.json
            pattern = r'spst_(\d+)-(\d+)'
            match = re.match(pattern, base_name)
            if match:
                self.chapter = int(match.group(1))
                self.stage_number = int(match.group(2))
                self.stage_type = 'spst'
                self.stage_id = f"spst_{self.chapter:02d}-{self.stage_number:02d}"
    
    def is_valid(self) -> bool:
        """Check if file was parsed successfully"""
        return self.chapter is not None and self.stage_type is not None
    
    def is_battle_story(self) -> bool:
        """Check if this is a battle story (beg/end)"""
        return self.stage_type in ['beg', 'end']
    
    def is_interlude(self) -> bool:
        """Check if this is an interlude story"""
        return self.stage_type in ['st', 'spst']


def scan_main_story_files(main_story_path: Path) -> List[MainStoryFile]:
    """Scan main story directory and return list of story files"""
    story_files = []
    
    if not main_story_path.exists():
        return story_files
    
    for filename in os.listdir(main_story_path):
        if not filename.endswith('.json'):
            continue
        
        file_path = main_story_path / filename
        story_file = MainStoryFile(filename, file_path)
        
        if story_file.is_valid():
            story_files.append(story_file)
    
    return story_files


def group_files_by_chapter(story_files: List[MainStoryFile]) -> Dict[int, List[MainStoryFile]]:
    """Group story files by chapter number"""
    chapters = {}
    
    for story_file in story_files:
        chapter = story_file.chapter
        if chapter not in chapters:
            chapters[chapter] = []
        chapters[chapter].append(story_file)
    
    # Sort files within each chapter
    for chapter in chapters:
        chapters[chapter].sort(key=lambda f: (f.stage_number, f.stage_type))
    
    return chapters


def create_main_story_activities(zones: Dict[str, ZoneInfo], 
                                available_chapters: List[int]) -> List[ActivityInfo]:
    """Create ActivityInfo objects for main story chapters"""
    activities = []
    
    for chapter in sorted(available_chapters):
        zone_id = f"main_{chapter}"
        zone_info = zones.get(zone_id)
        
        if zone_info and zone_info.is_main_story():
            activity = ActivityInfo.create_main_story(zone_info)
            activities.append(activity)
    
    return activities


def get_main_story_files_for_chapter(story_files: List[MainStoryFile], 
                                   chapter: int) -> List[str]:
    """Get list of story file names for specific chapter"""
    chapter_files = [f for f in story_files if f.chapter == chapter]
    chapter_files.sort(key=lambda f: (f.stage_number, f.stage_type))
    
    return [f.filename for f in chapter_files]