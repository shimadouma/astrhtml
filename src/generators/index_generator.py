"""Index page generator."""
from pathlib import Path
from typing import List

from .base_generator import BaseGenerator
from ..models.event import Event
from ..utils.date_formatter import format_timestamp
from ..config import DIST_PATH


class IndexGenerator(BaseGenerator):
    """Generator for index page."""
    
    def generate(self, events: List[Event], output_path: Path = DIST_PATH) -> None:
        """
        Generate index page.
        
        Args:
            events: List of events
            output_path: Output directory path
        """
        # Prepare event data for template
        events_data = []
        for event in events:
            event_data = {
                'event_id': event.event_id,
                'event_name': event.event_name,
                'activity_info': event.activity_info,
                'start_date': format_timestamp(event.activity_info.start_time),
                'end_date': format_timestamp(event.activity_info.end_time),
                'story_count': len(event.stories)
            }
            events_data.append(event_data)
        
        # Get relative paths (index is at root)
        index_file_path = output_path / 'index.html'
        paths = self.get_relative_paths(index_file_path, output_path)
        
        # Prepare context
        context = {
            'events': events_data,
            **paths
        }
        
        # Render and write
        html = self.render_template('index.html', context)
        self.write_html_file(html, index_file_path)
        
        print(f"Generated index page: {index_file_path}")