"""Search index generator for client-side search."""
import json
from pathlib import Path
from typing import List, Dict, Any

from .base_generator import BaseGenerator
from ..models.event import Event
from ..config import DIST_PATH


class SearchIndexGenerator(BaseGenerator):
    """Generator for search index."""
    
    def generate(self, events: List[Event], output_path: Path = DIST_PATH) -> None:
        """
        Generate search index for all events and stories.
        
        Args:
            events: List of event objects
            output_path: Output directory path
        """
        search_data = self._build_search_index(events)
        
        # Write search index as JSON
        search_file = output_path / 'static' / 'data' / 'search.json'
        search_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)
        
        print(f"Generated search index: {search_file}")
    
    def _build_search_index(self, events: List[Event]) -> Dict[str, Any]:
        """
        Build search index data structure.
        
        Args:
            events: List of events
            
        Returns:
            Search index data
        """
        index_data = {
            'events': [],
            'stories': []
        }
        
        for event in events:
            # Add event to index
            event_data = {
                'id': event.event_id,
                'name': event.event_name,
                'type': event.activity_info.display_type if event.activity_info else '',
                'start_date': event.activity_info.start_date.strftime('%Y-%m-%d') if event.activity_info else '',
                'end_date': event.activity_info.end_date.strftime('%Y-%m-%d') if event.activity_info else '',
                'url': f"events/{event.event_id}/index.html",
                'searchable_text': f"{event.event_name} {event.activity_info.display_type if event.activity_info else ''}"
            }
            index_data['events'].append(event_data)
            
            # Add stories to index
            stories = event.get_sorted_stories()
            for story in stories:
                # Extract searchable text from story content
                searchable_text = self._extract_story_text(story)
                
                story_data = {
                    'id': story.story_code,
                    'name': story.story_name,
                    'event_id': event.event_id,
                    'event_name': event.event_name,
                    'info': story.story_info or '',
                    'url': f"events/{event.event_id}/stories/{Path(story.story_code).stem if story.story_code else 'story'}.html",
                    'searchable_text': f"{story.story_name} {story.story_info or ''} {searchable_text}"
                }
                index_data['stories'].append(story_data)
        
        return index_data
    
    def _extract_story_text(self, story) -> str:
        """
        Extract searchable text from story content.
        
        Args:
            story: Story object
            
        Returns:
            Concatenated searchable text
        """
        text_parts = []
        
        for element in story.story_list:
            prop = element.prop.lower()
            
            if prop in ['name', 'dialog']:
                content = element.get_text()
                if content:
                    text_parts.append(content)
            elif prop == 'subtitle':
                subtitle = element.attributes.get('text')
                if subtitle:
                    text_parts.append(subtitle)
        
        # Join with spaces and limit length
        full_text = ' '.join(text_parts)
        # Limit to first 1000 characters for search index
        return full_text[:1000] if len(full_text) > 1000 else full_text