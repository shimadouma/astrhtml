"""Story parser module."""
from pathlib import Path
from typing import Optional, List

from ..models.story import Story, StoryElement
from ..models.event import Event
from .data_loader import load_story


def parse_story_file(file_path: Path) -> Optional[Story]:
    """
    Parse a story file.
    
    Args:
        file_path: Path to story JSON file
        
    Returns:
        Story object or None if error
    """
    data = load_story(file_path)
    
    if not data:
        return None
    
    try:
        return Story.from_dict(data)
    except (KeyError, TypeError) as e:
        print(f"Error parsing story {file_path}: {e}")
        return None


def parse_event_stories(event: Event) -> None:
    """
    Parse all stories for an event.
    
    Args:
        event: Event object with story_files
    """
    for story_file in event.story_files:
        story = parse_story_file(story_file)
        if story:
            event.add_story(story)


def create_stories_from_files(file_paths: List[Path]) -> List[Story]:
    """
    Create Story objects from list of file paths.
    
    Args:
        file_paths: List of paths to story JSON files
        
    Returns:
        List of Story objects
    """
    stories = []
    for file_path in file_paths:
        story = parse_story_file(file_path)
        if story:
            stories.append(story)
    return stories


def extract_story_content(story: Story) -> List[dict]:
    """
    Extract readable content from story.
    
    Args:
        story: Story object
        
    Returns:
        List of content dictionaries with type and text
    """
    content = []
    
    for elem in story.story_list:
        # Skip non-content elements
        if elem.prop in ['Dialog', 'dialog', 'Blocker', 'Delay', 
                        'delay', 'stopmusic', 'playMusic', 'HEADER']:
            continue
        
        # Process text content
        text = elem.get_text()
        if text:
            content_item = {
                'type': elem.prop,
                'text': text
            }
            
            # Add speaker if available
            speaker = elem.get_speaker()
            if speaker:
                content_item['speaker'] = speaker
            
            content.append(content_item)
        
        # Process background changes
        elif elem.is_background():
            image = elem.attributes.get('image')
            if image:
                content.append({
                    'type': 'background',
                    'image': image
                })
    
    return content


def get_story_summary(story: Story, max_length: int = 200) -> str:
    """
    Get a summary of the story.
    
    Args:
        story: Story object
        max_length: Maximum length of summary
        
    Returns:
        Story summary text
    """
    if story.story_info:
        return story.story_info[:max_length] if len(story.story_info) > max_length else story.story_info
    
    # Extract first few lines of dialog as summary
    dialogs = story.get_dialogs()
    summary_parts = []
    
    for dialog in dialogs[:3]:  # Get first 3 dialogs
        text = dialog.get_text()
        if text:
            summary_parts.append(text)
    
    summary = ' '.join(summary_parts)
    return summary[:max_length] if len(summary) > max_length else summary