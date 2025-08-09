"""Event page generator."""
from pathlib import Path
from typing import List

from .base_generator import BaseGenerator
from ..models.event import Event
from ..models.story import Story
from ..utils.date_formatter import format_timestamp
from ..config import DIST_PATH


class EventGenerator(BaseGenerator):
    """Generator for event pages."""
    
    def generate(self, event: Event, output_path: Path = DIST_PATH) -> None:
        """
        Generate event page.
        
        Args:
            event: Event object
            output_path: Output directory path
        """
        # Create event directory
        event_dir = output_path / 'events' / event.event_id
        event_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare stories data
        stories_data = []
        for story in event.get_sorted_stories():
            # Generate file name from story file path
            file_name = Path(story.story_code).stem if story.story_code else f"story_{len(stories_data)}"
            
            story_data = {
                'story_name': story.story_name,
                'story_code': story.story_code,
                'story_info': story.story_info,
                'file_name': file_name
            }
            stories_data.append(story_data)
        
        # Get relative paths
        event_index_path = event_dir / 'index.html'
        paths = self.get_relative_paths(event_index_path, output_path)
        
        # Prepare context
        context = {
            'event': {
                'event_id': event.event_id,
                'event_name': event.event_name,
                'activity_info': event.activity_info,
                'start_date': format_timestamp(event.activity_info.start_time),
                'end_date': format_timestamp(event.activity_info.end_time)
            },
            'stories': stories_data,
            **paths
        }
        
        # Render and write
        html = self.render_template('event.html', context)
        self.write_html_file(html, event_index_path)
        
        print(f"Generated event page: {event_index_path}")