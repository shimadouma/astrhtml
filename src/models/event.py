"""Event data model."""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from .activity import ActivityInfo
from .story import Story


@dataclass
class Event:
    """Represents an event with its stories."""
    
    activity_info: ActivityInfo
    story_files: List[Path] = field(default_factory=list)
    stories: List[Story] = field(default_factory=list)
    
    @property
    def event_id(self) -> str:
        """Get event ID."""
        return self.activity_info.id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return self.activity_info.name
    
    @property
    def has_stories(self) -> bool:
        """Check if event has story files."""
        return len(self.story_files) > 0
    
    def add_story_file(self, file_path: Path):
        """Add a story file path."""
        if file_path not in self.story_files:
            self.story_files.append(file_path)
    
    def add_story(self, story: Story):
        """Add a parsed story."""
        self.stories.append(story)
    
    def get_story_by_code(self, story_code: str) -> Optional[Story]:
        """Get story by its code."""
        for story in self.stories:
            if story.story_code == story_code:
                return story
        return None
    
    def get_sorted_stories(self) -> List[Story]:
        """Get stories sorted by story code."""
        return sorted(self.stories, key=lambda s: s.story_code)