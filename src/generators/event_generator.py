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
        
        # Load word count data
        from src.lib.wordcount_parser import (
            get_wordcount_mapping_for_event, 
            get_total_wordcount,
            format_wordcount
        )
        wordcount_mapping = get_wordcount_mapping_for_event(event.event_id)
        total_wordcount = get_total_wordcount(event.event_id)
        
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
                # First try to match by story code
                stage_code = stage_info.get('code', '')
                for s in event.stories:
                    if s.story_code == stage_code:
                        story = s
                        break
                
                # If no match by stage code, try matching by filename for hidden stories
                if not story:
                    story_file_name = Path(file_name).name
                    for story_file in event.story_files:
                        if story_file.name == story_file_name:
                            matching_file = story_file
                            # Find story that corresponds to this file (by index)
                            file_index = list(event.story_files).index(matching_file)
                            if file_index < len(event.stories):
                                story = event.stories[file_index]
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
                elif story.story_code and story.story_code.startswith('story_'):
                    # For hidden stories mapped to story_X pattern
                    actual_file_name = story.story_code
                    display_title = story.story_name if story.story_name else stage_info.get('name', f'隠しストーリー {story.story_code.split("_")[-1]}')
                else:
                    # Regular logic for non-MINISTORY events
                    actual_file_name = story.story_code if story.story_code else stage_info.get('code', Path(file_name).stem)
                    display_title = story.story_name
                
                # Get word count for this story
                # Try multiple filename patterns to match wordcount data
                story_base_name = Path(file_name).stem
                word_count = 0
                
                # Try different patterns to match with wordcount data
                patterns_to_try = [
                    story_base_name,  # Basic filename
                    file_name.replace('.json', ''),  # filename without extension
                    file_name.replace('level_', '').replace('.json', ''),  # without level_ prefix
                ]
                
                for pattern in patterns_to_try:
                    if pattern in wordcount_mapping:
                        word_count = wordcount_mapping[pattern]
                        break
                
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
                    'has_story': True,
                    'word_count': word_count,
                    'word_count_display': format_wordcount(word_count) if word_count else ''
                }
            else:
                # Handle virtual story entries (stages without story files but with generated story pages)
                stage_code = stage_info.get('code', '')
                
                if file_name.startswith('virtual_'):
                    # This is a virtual story entry for a stage without story files
                    # The story page should exist (generated by story generator), so we can link to it
                    print(f"Info: Virtual story entry for {file_name} (stage {stage_code})")
                    
                    story_data = {
                        'story_name': stage_info.get('name', f'ステージ {stage_code}'),
                        'story_code': stage_code,
                        'story_info': stage_info.get('description', ''),  # Use stage description if available
                        'file_name': stage_code,  # Link to the stage code HTML file (e.g., DM-7.html)
                        'stage_code': stage_code,
                        'stage_name': stage_info.get('name', f'ステージ {stage_code}'),
                        'story_phase': stage_info.get('story_phase', '戦闘後'),  # Default to post-battle
                        'danger_level': stage_info.get('danger_level', ''),
                        'stage_type': stage_info.get('stage_type', ''),
                        'has_story': True,  # The story page exists, so we can link to it
                        'word_count': 0,
                        'word_count_display': ''
                    }
                else:
                    # Story doesn't exist - create placeholder entry with no link
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
                        'has_story': False,
                        'word_count': 0,
                        'word_count_display': ''
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
                'end_date': format_timestamp(event.activity_info.end_time),
                'total_wordcount': total_wordcount,
                'total_wordcount_display': format_wordcount(total_wordcount) if total_wordcount else ''
            },
            'stories': stories_data,
            **paths
        }
        
        # Render and write
        html = self.render_template('event.html', context)
        self.write_html_file(html, event_index_path)
        
        print(f"Generated event page: {event_index_path}")