"""Story rendering utilities."""
from typing import List, Dict, Any, Optional
from ..models.story import Story, StoryElement
from .text_processor import process_dialog_text, escape_html


def render_story_element(element: StoryElement) -> Optional[Dict[str, Any]]:
    """
    Render a story element for HTML display.
    
    Args:
        element: Story element
        
    Returns:
        Rendered element data or None
    """
    prop = element.prop.lower()
    
    # Dialog or narration
    if prop in ['name', 'dialog']:
        text = element.get_text()
        if not text:
            return None
            
        speaker = element.get_speaker()
        
        return {
            'type': 'dialog',
            'speaker': speaker if speaker else None,
            'text': process_dialog_text(text),
            'is_narration': speaker is None
        }
    
    # Subtitle
    elif prop == 'subtitle':
        text = element.attributes.get('text')
        if not text:
            return None
            
        return {
            'type': 'subtitle',
            'text': process_dialog_text(text)
        }
    
    # Background change
    elif prop == 'background':
        image = element.attributes.get('image')
        if not image:
            return None
            
        return {
            'type': 'background',
            'image': image,
            'description': f"背景: {image}"
        }
    
    # Character appearance
    elif prop == 'character':
        names = []
        if 'name' in element.attributes:
            names.append(element.attributes['name'])
        if 'name2' in element.attributes:
            names.append(element.attributes['name2'])
            
        if not names:
            return None
            
        return {
            'type': 'character',
            'characters': names,
            'focus': element.attributes.get('focus')
        }
    
    return None


def render_story_content(story: Story) -> List[Dict[str, Any]]:
    """
    Render all story content for HTML display.
    
    Args:
        story: Story object
        
    Returns:
        List of rendered content elements
    """
    rendered_content = []
    
    for element in story.story_list:
        rendered = render_story_element(element)
        if rendered:
            rendered_content.append(rendered)
    
    return rendered_content


def group_consecutive_dialogs(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group consecutive dialogs from the same speaker, including subtitles.
    
    Args:
        content: List of rendered content
        
    Returns:
        Content with grouped consecutive dialogs
    """
    if not content:
        return []
    
    grouped_content = []
    current_group = None
    
    for item in content:
        if item['type'] in ['dialog', 'subtitle']:
            # For subtitles, treat as narration without speaker
            if item['type'] == 'subtitle':
                speaker = None
                is_narration = True
                text = item['text']
            else:
                speaker = item.get('speaker')
                is_narration = item.get('is_narration', False)
                text = item['text']
            
            # Start new group or continue existing one
            if (current_group is None or 
                current_group['type'] not in ['dialog', 'subtitle'] or
                current_group.get('speaker') != speaker or
                current_group.get('is_narration') != is_narration):
                
                # Save previous group
                if current_group:
                    grouped_content.append(current_group)
                
                # Start new group - use 'dialog' type for both dialog and subtitle
                current_group = {
                    'type': 'dialog',
                    'speaker': speaker,
                    'texts': [text],
                    'is_narration': is_narration
                }
            else:
                # Add to existing group
                current_group['texts'].append(text)
        else:
            # Save current group and add non-dialog item
            if current_group:
                grouped_content.append(current_group)
                current_group = None
            grouped_content.append(item)
    
    # Add final group
    if current_group:
        grouped_content.append(current_group)
    
    return grouped_content


def group_dialog_by_scene(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group dialog content by scene (background changes) and group consecutive dialogs.
    
    Args:
        content: List of rendered content
        
    Returns:
        Content grouped by scenes with consecutive dialogs merged
    """
    scenes = []
    current_scene = {
        'background': None,
        'content': []
    }
    
    for item in content:
        if item['type'] == 'background':
            # Group consecutive dialogs in current scene before starting new scene
            if current_scene['content']:
                current_scene['content'] = group_consecutive_dialogs(current_scene['content'])
                scenes.append(current_scene)
            current_scene = {
                'background': item['image'],
                'content': []
            }
        else:
            current_scene['content'].append(item)
    
    # Add last scene with grouped dialogs
    if current_scene['content']:
        current_scene['content'] = group_consecutive_dialogs(current_scene['content'])
        scenes.append(current_scene)
    
    return scenes