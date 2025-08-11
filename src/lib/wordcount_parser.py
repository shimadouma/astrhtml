"""Word count parser for story files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from src.config import ARKNIGHTS_STORY_JSON_PATH


def load_wordcount_data() -> Dict[str, Dict[str, int]]:
    """Load word count data from wordcount.json.
    
    Returns:
        Dictionary mapping event_id to story file paths and their word counts
    """
    wordcount_path = ARKNIGHTS_STORY_JSON_PATH / "wordcount.json"
    
    if not wordcount_path.exists():
        print(f"Warning: wordcount.json not found at {wordcount_path}")
        return {}
    
    try:
        with open(wordcount_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading wordcount.json: {e}")
        return {}


def get_story_wordcount(event_id: str, story_file: str, 
                        wordcount_data: Optional[Dict] = None) -> Optional[int]:
    """Get word count for a specific story file.
    
    Args:
        event_id: Event ID
        story_file: Story file name (without extension)
        wordcount_data: Preloaded wordcount data (optional)
    
    Returns:
        Word count or None if not found
    """
    if wordcount_data is None:
        wordcount_data = load_wordcount_data()
    
    if event_id not in wordcount_data:
        return None
    
    event_data = wordcount_data[event_id]
    
    # Try different path patterns
    patterns = [
        f"activities/{event_id}/{story_file}",
        f"activities/{event_id}/level_{story_file}",
        story_file,
        f"level_{story_file}"
    ]
    
    for pattern in patterns:
        if pattern in event_data:
            return event_data[pattern]
    
    # Try to find by partial match
    for path, count in event_data.items():
        if story_file in path or path.endswith(f"/{story_file}"):
            return count
    
    return None


def get_event_story_order(event_id: str, 
                         wordcount_data: Optional[Dict] = None) -> List[str]:
    """Get story order for an event from wordcount.json.
    
    Args:
        event_id: Event ID
        wordcount_data: Preloaded wordcount data (optional)
    
    Returns:
        List of story file names in order
    """
    if wordcount_data is None:
        wordcount_data = load_wordcount_data()
    
    if event_id not in wordcount_data:
        return []
    
    event_data = wordcount_data[event_id]
    
    # Extract file names from paths and maintain order
    story_files = []
    for path in event_data.keys():
        # Extract filename from path
        filename = path.split('/')[-1]
        # Remove 'level_' prefix if present
        if filename.startswith('level_'):
            filename = filename[6:]
        story_files.append(filename)
    
    return story_files


def get_total_wordcount(event_id: str, 
                        wordcount_data: Optional[Dict] = None) -> int:
    """Get total word count for an event.
    
    Args:
        event_id: Event ID
        wordcount_data: Preloaded wordcount data (optional)
    
    Returns:
        Total word count for the event
    """
    if wordcount_data is None:
        wordcount_data = load_wordcount_data()
    
    if event_id not in wordcount_data:
        return 0
    
    return sum(wordcount_data[event_id].values())


def extract_story_filename_from_path(path: str) -> str:
    """Extract story filename from wordcount.json path.
    
    Args:
        path: Path from wordcount.json
    
    Returns:
        Story filename without extension
    """
    filename = path.split('/')[-1]
    # Remove 'level_' prefix if present
    if filename.startswith('level_'):
        filename = filename[6:]
    return filename


def get_wordcount_mapping_for_event(event_id: str,
                                   wordcount_data: Optional[Dict] = None) -> Dict[str, int]:
    """Get a mapping of story filenames to word counts for an event.
    
    Args:
        event_id: Event ID
        wordcount_data: Preloaded wordcount data (optional)
    
    Returns:
        Dictionary mapping story filenames to word counts
    """
    if wordcount_data is None:
        wordcount_data = load_wordcount_data()
    
    if event_id not in wordcount_data:
        return {}
    
    event_data = wordcount_data[event_id]
    mapping = {}
    
    for path, count in event_data.items():
        filename = extract_story_filename_from_path(path)
        mapping[filename] = count
    
    return mapping


def format_wordcount(count: int) -> str:
    """Format word count for display.
    
    Args:
        count: Word count
    
    Returns:
        Formatted string (e.g., "2,645文字")
    """
    if count == 0:
        return ""
    return f"{count:,}文字"