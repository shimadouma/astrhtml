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
            
            # For MINISTORY and TYPE_ACT4D0 events, match by filename since story_code is empty
            if event.activity_info.type in ['MINISTORY', 'TYPE_ACT4D0']:
                story_file_name = Path(file_name).name
                # Find the matching story file
                matching_file = None
                for story_file in event.story_files:
                    if story_file.name == story_file_name:
                        matching_file = story_file
                        break
                
                if matching_file:
                    # Find story that corresponds to this file (by index)
                    file_index = list(event.story_files).index(matching_file)
                    if file_index < len(event.stories):
                        story = event.stories[file_index]
            else:
                # Regular matching for non-MINISTORY events
                for s in event.stories:
                    # Match by story code instead of file name
                    stage_code = stage_info.get('code', '')
                    if s.story_code == stage_code:
                        story = s
                        break
            
            # Generate story data
            if story:
                # For MINISTORY and TYPE_ACT4D0 events, use different filename and title logic
                if event.activity_info.type == 'MINISTORY':
                    # Use stage code as filename for MINISTORY (ST-1, ST-2, etc.)
                    actual_file_name = stage_info.get('code', Path(file_name).stem)
                    # Use the actual story name from the JSON file
                    display_title = story.story_name if story.story_name else stage_info.get('name', f'ストーリー {stage_info.get("code", "")}')
                elif event.activity_info.type == 'TYPE_ACT4D0':
                    # For TYPE_ACT4D0, map JSON filename to HTML filename using story index
                    file_index = list(event.story_files).index(matching_file)
                    actual_file_name = f"story_{file_index}"
                    # Use the actual story name from JSON storyName field
                    display_title = story.story_name if story.story_name else stage_info.get('name', f'シナリオ {file_index + 1}')
                else:
                    # Regular logic for non-MINISTORY events
                    actual_file_name = story.story_code if story.story_code else stage_info.get('code', Path(file_name).stem)
                    display_title = story.story_name
                
                story_data = {
                    'story_name': display_title,
                    'story_code': story.story_code if story.story_code else stage_info.get('code', ''),
                    'story_info': story.story_info,
                    'file_name': actual_file_name,
                    'stage_code': stage_info.get('code', ''),
                    'stage_name': display_title,
                    'story_phase': stage_info.get('story_phase', ''),
                    'danger_level': stage_info.get('danger_level', ''),
                    'stage_type': stage_info.get('stage_type', ''),
                    'has_story': True
                }
            else:
                # Story doesn't exist - create placeholder entry
                stage_code = stage_info.get('code', '')
                print(f"Info: No story data for {file_name} (stage {stage_code}), creating placeholder entry")
                
                story_data = {
                    'story_name': 'ストーリーなし',
                    'story_code': stage_code,
                    'story_info': '',
                    'file_name': '',  # No file to link to
                    'stage_code': stage_code,
                    'stage_name': stage_info.get('name', f'ステージ {stage_code}'),
                    'story_phase': stage_info.get('story_phase', ''),
                    'danger_level': stage_info.get('danger_level', ''),
                    'stage_type': stage_info.get('stage_type', ''),
                    'has_story': False
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