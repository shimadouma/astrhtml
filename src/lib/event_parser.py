"""Event parser module."""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..models.activity import ActivityInfo
from ..models.event import Event
from .data_loader import load_activity_table, get_story_files
from .stage_parser import load_stage_table, get_story_order_for_event, get_stage_display_info, StageInfo


def parse_activities(base_path: Path) -> Dict[str, ActivityInfo]:
    """
    Parse all activities from activity_table.json.
    
    Args:
        base_path: Base path to ArknightsStoryJson data
        
    Returns:
        Dictionary of activity_id -> ActivityInfo
    """
    activities_data = load_activity_table(base_path)
    activities = {}
    
    for activity_id, activity_data in activities_data.items():
        try:
            activity = ActivityInfo.from_dict(activity_data)
            activities[activity_id] = activity
        except (KeyError, TypeError) as e:
            print(f"Error parsing activity {activity_id}: {e}")
            continue
    
    return activities


def get_events_with_stories(base_path: Path) -> List[Event]:
    """
    Get all events that have story files.
    
    Args:
        base_path: Base path to ArknightsStoryJson data
        
    Returns:
        List of Event objects with story files
    """
    activities = parse_activities(base_path)
    events = []
    
    for activity_id, activity_info in activities.items():
        # Skip activities without stages
        if not activity_info.has_stage:
            continue
            
        # Get story files for this event
        story_files = get_story_files(activity_id, base_path)
        
        if story_files:
            event = Event(
                activity_info=activity_info,
                story_files=story_files
            )
            events.append(event)
    
    return events


def filter_events_by_type(events: List[Event], display_type: Optional[str] = None) -> List[Event]:
    """
    Filter events by display type.
    
    Args:
        events: List of events
        display_type: Display type to filter by (e.g., 'SIDESTORY')
        
    Returns:
        Filtered list of events
    """
    if not display_type:
        return events
    
    return [
        event for event in events 
        if event.activity_info.display_type == display_type
    ]


def sort_events_by_date(events: List[Event], reverse: bool = True) -> List[Event]:
    """
    Sort events by start date.
    
    Args:
        events: List of events
        reverse: If True, sort newest first
        
    Returns:
        Sorted list of events
    """
    return sorted(
        events,
        key=lambda e: e.activity_info.start_time,
        reverse=reverse
    )


def get_ordered_stories_for_event(event_id: str, base_path: Path) -> List[Tuple[str, Dict[str, str]]]:
    """
    Get story files for an event in correct order with display information
    
    Args:
        event_id: Event ID
        base_path: Base path to ArknightsStoryJson data
        
    Returns:
        List of (story_file_name, display_info) tuples in correct order
    """
    # Load stage table
    stages = load_stage_table(base_path)
    
    # Get story files (pass parent directory of base_path)
    story_files = get_story_files(event_id, base_path.parent)
    
    # Convert Path objects to filename strings
    story_file_names = [path.name for path in story_files]
    
    if not story_file_names or not stages:
        # fallback: alphabetical order
        return [(file_name, {'code': '', 'name': file_name, 'story_phase': '', 'danger_level': '', 'stage_type': ''}) 
                for file_name in sorted(story_file_names)]
    
    # Get in correct order
    ordered_stories = get_story_order_for_event(event_id, stages, story_file_names)
    
    result = []
    for file_name, stage_info, is_battle_story in ordered_stories:
        # Determine story type
        story_type = 'story'
        if is_battle_story:
            if '_beg' in file_name:
                story_type = 'beg'
            elif '_end' in file_name:
                story_type = 'end'
        
        # Generate display information
        display_info = get_stage_display_info(stage_info, story_type)
        result.append((file_name, display_info))
    
    return result