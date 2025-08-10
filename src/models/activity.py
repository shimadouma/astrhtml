"""Activity table data model."""
from dataclasses import dataclass
from typing import Optional, List, Union
from datetime import datetime
from .zone_info import ZoneInfo


@dataclass
class ActivityInfo:
    """Represents an activity/event from activity_table.json."""
    
    id: str
    type: str
    display_type: str
    name: str
    start_time: int
    end_time: int
    reward_end_time: int
    display_on_home: bool
    has_stage: bool
    template_shop_id: Optional[str]
    medal_group_id: Optional[str]
    ungroupe_medal_ids: Optional[List[str]]
    is_replicate: bool
    need_fixed_sync: bool
    trap_domain_id: Optional[str]
    rec_type: str
    is_page_entry: bool
    is_magnify: bool
    
    # Main story specific fields
    zone_info: Optional[ZoneInfo] = None
    is_main_story: bool = False
    
    @property
    def start_date(self) -> datetime:
        """Convert start_time to datetime."""
        return datetime.fromtimestamp(self.start_time)
    
    @property
    def end_date(self) -> datetime:
        """Convert end_time to datetime."""
        return datetime.fromtimestamp(self.end_time)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActivityInfo':
        """Create ActivityInfo from dictionary."""
        return cls(
            id=data['id'],
            type=data['type'],
            display_type=data.get('displayType', 'NONE'),
            name=data['name'],
            start_time=data['startTime'],
            end_time=data['endTime'],
            reward_end_time=data['rewardEndTime'],
            display_on_home=data.get('displayOnHome', False),
            has_stage=data.get('hasStage', False),
            template_shop_id=data.get('templateShopId'),
            medal_group_id=data.get('medalGroupId'),
            ungroupe_medal_ids=data.get('ungroupedMedalIds'),
            is_replicate=data.get('isReplicate', False),
            need_fixed_sync=data.get('needFixedSync', False),
            trap_domain_id=data.get('trapDomainId'),
            rec_type=data.get('recType', 'NONE'),
            is_page_entry=data.get('isPageEntry', False),
            is_magnify=data.get('isMagnify', False)
        )
    
    @classmethod
    def create_main_story(cls, zone_info: ZoneInfo) -> 'ActivityInfo':
        """Create ActivityInfo for main story chapter."""
        return cls(
            id=f"main_{zone_info.chapter_number:02d}",
            type="MAIN_STORY",
            display_type="MAIN_STORY", 
            name=zone_info.display_title,
            start_time=0,  # Main story has no time limit
            end_time=0,
            reward_end_time=0,
            display_on_home=True,
            has_stage=True,
            template_shop_id=None,
            medal_group_id=None,
            ungroupe_medal_ids=None,
            is_replicate=False,
            need_fixed_sync=False,
            trap_domain_id=None,
            rec_type="MAIN",
            is_page_entry=True,
            is_magnify=False,
            zone_info=zone_info,
            is_main_story=True
        )