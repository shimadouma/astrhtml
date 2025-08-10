"""Index page generator."""
from pathlib import Path
from typing import List, Optional

from .base_generator import BaseGenerator
from ..models.event import Event
from ..models.activity import ActivityInfo
from ..utils.date_formatter import format_timestamp
from ..config import DIST_PATH


class IndexGenerator(BaseGenerator):
    """Generator for index page."""
    
    def generate(self, events: List[Event], main_story_activities: Optional[List[ActivityInfo]] = None, 
                 output_path: Path = DIST_PATH) -> None:
        """
        Generate index page.
        
        Args:
            events: List of events
            main_story_activities: List of main story activities (optional)
            output_path: Output directory path
        """
        # Prepare all items (events + main story) as cards
        all_cards = []
        
        # Add main story chapters as cards first
        if main_story_activities:
            for activity in sorted(main_story_activities, key=lambda a: a.zone_info.chapter_number if a.zone_info else 0):
                if activity.zone_info:
                    card_data = {
                        'type': 'main_story',
                        'id': f"main_{activity.zone_info.chapter_number:02d}",
                        'title': activity.zone_info.display_title,
                        'subtitle': activity.zone_info.zone_name_second,
                        'link': f"main/chapter_{activity.zone_info.chapter_number:02d}/index.html",
                        'can_access': activity.zone_info.can_preview,
                        'chapter_number': activity.zone_info.chapter_number,
                        'sort_key': f"main_{activity.zone_info.chapter_number:04d}"
                    }
                    all_cards.append(card_data)
        
        # Add events as cards
        for event in events:
            card_data = {
                'type': 'event',
                'id': event.event_id,
                'title': event.event_name,
                'subtitle': event.activity_info.display_type,
                'link': f"events/{event.event_id}/index.html",
                'can_access': True,
                'start_date': format_timestamp(event.activity_info.start_time),
                'end_date': format_timestamp(event.activity_info.end_time),
                'story_count': len(event.stories),
                'sort_key': f"event_{event.activity_info.start_time}"
            }
            all_cards.append(card_data)
        
        # Sort cards: main story first (by chapter), then events (by date, newest first)
        all_cards.sort(key=lambda card: (
            0 if card['type'] == 'main_story' else 1,
            card['sort_key'] if card['type'] == 'main_story' else -int(card['sort_key'].split('_')[1])
        ))
        
        # Get relative paths (index is at root)
        index_file_path = output_path / 'index.html'
        paths = self.get_relative_paths(index_file_path, output_path)
        
        # Prepare context
        context = {
            'all_cards': all_cards,
            'has_cards': bool(all_cards),
            **paths
        }
        
        # Render and write
        html = self.render_template('index.html', context)
        self.write_html_file(html, index_file_path)
        
        print(f"Generated index page: {index_file_path}")