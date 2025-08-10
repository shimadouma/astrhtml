from dataclasses import dataclass
from typing import Optional

@dataclass
class ZoneInfo:
    """Information about a main story zone/chapter"""
    zone_id: str
    zone_index: int
    zone_type: str
    zone_name_first: str  # e.g., "序章", "第一章"
    zone_name_second: str  # e.g., "暗黒時代・上"
    zone_name_title_current: str  # e.g., "00", "01"
    zone_name_title_ex: str  # e.g., "EPISODE"
    zone_name_third: str  # e.g., "EPISODE 00"
    locked_text: str
    can_preview: bool
    
    @property
    def chapter_number(self) -> int:
        """Get chapter number as integer"""
        if self.zone_id.startswith('main_'):
            return int(self.zone_id.replace('main_', ''))
        return 0
    
    @property
    def display_title(self) -> str:
        """Get display title for the chapter"""
        return f"{self.zone_name_first} {self.zone_name_second}"
    
    @property
    def short_title(self) -> str:
        """Get short title for navigation"""
        return self.zone_name_first
    
    @property
    def episode_title(self) -> str:
        """Get episode title"""
        return self.zone_name_third
    
    def is_main_story(self) -> bool:
        """Check if this is a main story zone"""
        return self.zone_type == "MAINLINE"