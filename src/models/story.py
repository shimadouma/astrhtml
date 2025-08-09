"""Story data model."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class StoryElement:
    """Represents a single element in the story list."""
    
    id: int
    prop: str
    attributes: Dict[str, Any]
    figure_art: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StoryElement':
        """Create StoryElement from dictionary."""
        return cls(
            id=data['id'],
            prop=data['prop'],
            attributes=data.get('attributes', {}),
            figure_art=data.get('figure_art')
        )
    
    def is_dialog(self) -> bool:
        """Check if this is a dialog element."""
        return self.prop.lower() in ['dialog', 'name']
    
    def is_character(self) -> bool:
        """Check if this is a character element."""
        return self.prop == 'Character'
    
    def is_subtitle(self) -> bool:
        """Check if this is a subtitle element."""
        return self.prop == 'Subtitle'
    
    def is_background(self) -> bool:
        """Check if this is a background element."""
        return self.prop == 'Background'
    
    def get_text(self) -> Optional[str]:
        """Get text content from the element."""
        if self.is_dialog() or self.prop == 'name':
            return self.attributes.get('content', self.attributes.get('text'))
        elif self.is_subtitle():
            return self.attributes.get('text')
        return None
    
    def get_speaker(self) -> Optional[str]:
        """Get speaker name if available."""
        if self.prop == 'name':
            return self.attributes.get('name')
        return None


@dataclass
class Story:
    """Represents a complete story."""
    
    lang: str
    event_id: str
    event_name: str
    entry_type: str
    story_code: str
    avg_tag: str
    story_name: str
    story_info: str
    story_list: List[StoryElement] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Story':
        """Create Story from dictionary."""
        story_list = [
            StoryElement.from_dict(elem) 
            for elem in data.get('storyList', [])
        ]
        
        return cls(
            lang=data.get('lang', 'ja_JP'),
            event_id=data.get('eventid', ''),
            event_name=data.get('eventName', ''),
            entry_type=data.get('entryType', ''),
            story_code=data.get('storyCode', ''),
            avg_tag=data.get('avgTag', ''),
            story_name=data.get('storyName', ''),
            story_info=data.get('storyInfo', ''),
            story_list=story_list
        )
    
    def get_dialogs(self) -> List[StoryElement]:
        """Get all dialog elements."""
        return [elem for elem in self.story_list if elem.is_dialog()]
    
    def get_characters(self) -> List[str]:
        """Get unique list of character names."""
        characters = set()
        for elem in self.story_list:
            speaker = elem.get_speaker()
            if speaker:
                characters.add(speaker)
        return sorted(list(characters))