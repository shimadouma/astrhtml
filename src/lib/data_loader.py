"""Data loader module for JSON files."""
import json
from pathlib import Path
from typing import Any, Dict, Optional, List


def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def load_activity_table(base_path: Path) -> Dict[str, Any]:
    """
    Load activity table data.
    
    Args:
        base_path: Base path to ArknightsStoryJson data
        
    Returns:
        Activity table data
    """
    activity_table_path = base_path / 'ja_JP' / 'gamedata' / 'excel' / 'activity_table.json'
    data = load_json(activity_table_path)
    
    if not data or 'basicInfo' not in data:
        return {}
    
    return data['basicInfo']


def get_story_files(event_id: str, base_path: Path) -> List[Path]:
    """
    Get all story files for an event.
    
    Args:
        event_id: Event ID
        base_path: Base path to ArknightsStoryJson data
        
    Returns:
        List of story file paths
    """
    story_dir = base_path / 'ja_JP' / 'gamedata' / 'story' / 'activities' / event_id
    
    if not story_dir.exists():
        return []
    
    # Get all JSON files in the directory
    story_files = sorted(story_dir.glob('*.json'))
    return story_files


def load_story(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load story data from file.
    
    Args:
        file_path: Path to story JSON file
        
    Returns:
        Story data or None if error
    """
    return load_json(file_path)