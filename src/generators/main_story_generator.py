"""Main story chapter page generator."""
from pathlib import Path
from typing import List, Dict, Any

from .base_generator import BaseGenerator
from ..models.activity import ActivityInfo
from ..models.zone_info import ZoneInfo
from ..models.story import Story
from ..lib.main_story_parser import MainStoryFile, get_main_story_files_for_chapter
from ..lib.stage_parser import get_main_story_order_for_chapter, get_main_story_display_info, StageInfo
from ..lib.story_parser import create_stories_from_files
from ..config import DIST_PATH, ARKNIGHTS_STORY_JSON_PATH


class MainStoryGenerator(BaseGenerator):
    """Generator for main story chapter pages."""
    
    def generate_chapter(self, activity: ActivityInfo, stages: Dict[str, StageInfo], 
                        story_files: List[MainStoryFile], output_path: Path = DIST_PATH) -> None:
        """
        Generate main story chapter page.
        
        Args:
            activity: ActivityInfo object for the chapter
            stages: Dictionary of stage information
            story_files: List of story files for this chapter
            output_path: Output directory path
        """
        if not activity.zone_info:
            return
        
        chapter = activity.zone_info.chapter_number
        
        # Create chapter directory
        chapter_dir = output_path / 'main' / f'chapter_{chapter:02d}'
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        # Get story filenames for this chapter
        chapter_story_files = get_main_story_files_for_chapter(story_files, chapter)
        
        # Get ordered stories with stage information
        ordered_stories = get_main_story_order_for_chapter(chapter, stages, chapter_story_files)
        
        # Create story objects
        story_file_paths = []
        for file_name in chapter_story_files:
            story_path = ARKNIGHTS_STORY_JSON_PATH / "gamedata" / "story" / "obt" / "main" / file_name
            story_file_paths.append(story_path)
        
        stories = create_stories_from_files(story_file_paths)
        # Create mapping using file path as key
        story_dict = {}
        for i, story in enumerate(stories):
            if story and i < len(story_file_paths):
                file_name = story_file_paths[i].name
                story_dict[file_name] = story
        
        # Prepare stories data for template
        stories_data = []
        for file_name, stage_info, is_battle_story in ordered_stories:
            # Find corresponding story object using file name
            story = story_dict.get(file_name)
            
            if story:
                # Extract story type from filename for display
                story_type = 'story'  # default
                base_name = file_name.replace('level_', '').replace('.json', '')
                if '_beg' in base_name:
                    story_type = 'beg'
                elif '_end' in base_name:
                    story_type = 'end'
                
                # Get display info
                display_info = get_main_story_display_info(stage_info, story_type)
                
                # Use the same filename logic as story generator
                story_file_name = Path(story.story_code).stem if story.story_code else f"story_{file_name}"
                
                story_data = {
                    'story_name': story.story_name,
                    'story_code': story.story_code,
                    'file_name': story_file_name,
                    'is_battle_story': is_battle_story,
                    'stage_code': stage_info.code,
                    'stage_name': stage_info.name,
                    'danger_level': stage_info.danger_level,
                    'story_phase': display_info.get('story_phase', ''),
                    'has_story': True
                }
                stories_data.append(story_data)
            else:
                # Story doesn't exist - create placeholder entry
                print(f"Info: No story data for {file_name} (stage {stage_info.code}), creating placeholder entry")
                
                story_data = {
                    'story_name': 'ストーリーなし',
                    'story_code': stage_info.code,
                    'file_name': '',  # No file to link to
                    'is_battle_story': is_battle_story,
                    'stage_code': stage_info.code,
                    'stage_name': stage_info.name,
                    'danger_level': stage_info.danger_level,
                    'story_phase': '',
                    'has_story': False
                }
                stories_data.append(story_data)
        
        # Template data
        template_data = {
            'activity': activity,
            'zone_info': activity.zone_info,
            'chapter': chapter,
            'chapter_title': activity.zone_info.display_title,
            'episode_title': activity.zone_info.episode_title,
            'stories': stories_data,
            'css_path': '../../static/css/',
            'js_path': '../../static/js/',
            'index_path': '../../index.html',
            'root_path': '../../'
        }
        
        # Render template
        template = self.env.get_template('main_story_chapter.html')
        html_content = template.render(**template_data)
        
        # Write HTML file
        output_file = chapter_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_main_index(self, activities: List[ActivityInfo], 
                           output_path: Path = DIST_PATH) -> None:
        """
        Generate main story index page.
        
        Args:
            activities: List of main story ActivityInfo objects
            output_path: Output directory path
        """
        # Create main story directory
        main_dir = output_path / 'main'
        main_dir.mkdir(parents=True, exist_ok=True)
        
        # Sort activities by chapter number
        sorted_activities = sorted(
            activities, 
            key=lambda a: a.zone_info.chapter_number if a.zone_info else 0
        )
        
        # Prepare chapters data
        chapters_data = []
        for activity in sorted_activities:
            if activity.zone_info:
                chapter_data = {
                    'id': activity.id,
                    'chapter': activity.zone_info.chapter_number,
                    'title': activity.zone_info.display_title,
                    'subtitle': activity.zone_info.zone_name_second,
                    'episode_title': activity.zone_info.episode_title,
                    'short_title': activity.zone_info.short_title,
                    'can_preview': activity.zone_info.can_preview,
                    'locked_text': activity.zone_info.locked_text
                }
                chapters_data.append(chapter_data)
        
        # Template data
        template_data = {
            'chapters': chapters_data,
            'css_path': '../static/css/',
            'js_path': '../static/js/',
            'index_path': '../index.html',
            'root_path': '../'
        }
        
        # Render template
        template = self.env.get_template('main_story_index.html')
        html_content = template.render(**template_data)
        
        # Write HTML file
        output_file = main_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)