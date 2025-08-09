"""Event page generator."""
from pathlib import Path
from typing import List

from .base_generator import BaseGenerator
from ..models.event import Event
from ..models.story import Story
from ..utils.date_formatter import format_timestamp
from ..lib.event_parser import get_ordered_stories_for_event
from ..config import DIST_PATH, ARKNIGHTS_STORY_JSON_PATH


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
        
        # Get ordered stories with stage information
        ordered_stories = get_ordered_stories_for_event(event.event_id, ARKNIGHTS_STORY_JSON_PATH)
        
        # Prepare stories data
        stories_data = []
        for file_name, stage_info in ordered_stories:
            # Find corresponding story object
            story = None
            for s in event.stories:
                story_file_name = Path(s.story_code).name if s.story_code else ""
                if story_file_name == file_name:
                    story = s
                    break
            
            # Generate story data
            # Use the same file name logic as story_generator
            actual_file_name = Path(file_name).stem if story and story.story_code else stage_info.get('code', Path(file_name).stem)
            
            if story:
                story_data = {
                    'story_name': story.story_name,
                    'story_code': story.story_code,
                    'story_info': story.story_info,
                    'file_name': actual_file_name,
                    'stage_code': stage_info.get('code', ''),
                    'stage_name': stage_info.get('name', story.story_name),
                    'story_phase': stage_info.get('story_phase', ''),
                    'danger_level': stage_info.get('danger_level', ''),
                    'stage_type': stage_info.get('stage_type', '')
                }
            else:
                # Fallback if story object not found
                story_data = {
                    'story_name': stage_info.get('name', file_name),
                    'story_code': file_name,
                    'story_info': '',
                    'file_name': actual_file_name,
                    'stage_code': stage_info.get('code', ''),
                    'stage_name': stage_info.get('name', file_name),
                    'story_phase': stage_info.get('story_phase', ''),
                    'danger_level': stage_info.get('danger_level', ''),
                    'stage_type': stage_info.get('stage_type', '')
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