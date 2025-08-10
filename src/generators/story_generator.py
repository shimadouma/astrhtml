"""Story page generator."""
from pathlib import Path
from typing import List, Optional, Union

from .base_generator import BaseGenerator
from ..models.event import Event
from ..models.story import Story
from ..models.activity import ActivityInfo
from ..utils.story_renderer import render_story_content, group_dialog_by_scene
from ..config import DIST_PATH


class StoryGenerator(BaseGenerator):
    """Generator for story pages."""
    
    def generate(self, event: Event, output_path: Path = DIST_PATH) -> None:
        """
        Generate all story pages for an event.
        
        Args:
            event: Event object with stories
            output_path: Output directory path
        """
        # Create stories directory
        stories_dir = output_path / 'events' / event.event_id / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        
        # Get stories in correct order for MINISTORY and TYPE_ACT4D0 vs regular events
        if event.activity_info.type in ['MINISTORY', 'TYPE_ACT4D0']:
            # For MINISTORY and TYPE_ACT4D0 events, preserve the original file order since stories are already ordered correctly
            stories = event.stories
        else:
            # Get sorted stories for regular events
            stories = event.get_sorted_stories()
        
        # Generate each story page
        for i, story in enumerate(stories):
            # Determine file name based on event type and story code
            if event.activity_info.type == 'MINISTORY':
                # For MINISTORY, use ST-1, ST-2, etc. as filename
                file_name = f"ST-{i+1}"
            elif event.activity_info.type == 'TYPE_ACT4D0':
                # For TYPE_ACT4D0, use story_0, story_1, etc. as filename (0-indexed)
                file_name = f"story_{i}"
            elif story.story_code and story.story_code.startswith('story_'):
                # For hidden stories mapped to story_X pattern
                file_name = story.story_code
            else:
                # Regular logic for other events
                file_name = Path(story.story_code).stem if story.story_code else f"story_{i}"
            
            # Get previous and next stories
            prev_story = None
            next_story = None
            
            if i > 0:
                if hasattr(event, 'activity_info') and event.activity_info.type == 'MINISTORY':
                    prev_file_name = f"ST-{i}"
                else:
                    prev_story_code = stories[i-1].story_code
                    prev_file_name = Path(prev_story_code).stem if prev_story_code else f"story_{i-1}"
                
                prev_story = {
                    'story_name': stories[i-1].story_name,
                    'file_name': prev_file_name
                }
            
            if i < len(stories) - 1:
                if hasattr(event, 'activity_info') and event.activity_info.type == 'MINISTORY':
                    next_file_name = f"ST-{i+2}"
                else:
                    next_story_code = stories[i+1].story_code
                    next_file_name = Path(next_story_code).stem if next_story_code else f"story_{i+1}"
                
                next_story = {
                    'story_name': stories[i+1].story_name,
                    'file_name': next_file_name
                }
            
            # Generate story page
            self._generate_story_page(
                story, 
                event,
                stories_dir / f"{file_name}.html",
                output_path,
                prev_story,
                next_story
            )
    
    def _generate_story_page(
        self,
        story: Story,
        event: Event,
        output_file: Path,
        root_path: Path,
        prev_story: Optional[dict] = None,
        next_story: Optional[dict] = None
    ) -> None:
        """
        Generate a single story page.
        
        Args:
            story: Story object
            event: Parent event object
            output_file: Output file path
            root_path: Root directory path
            prev_story: Previous story info
            next_story: Next story info
        """
        # Render story content
        rendered_content = render_story_content(story)
        
        # Group content by scenes
        scenes = group_dialog_by_scene(rendered_content)
        
        # Get relative paths
        paths = self.get_relative_paths(output_file, root_path)
        
        # Add event index path
        event_index_path = '../index.html'
        
        # Prepare context
        context = {
            'story': story,
            'scenes': scenes,
            'event_index_path': event_index_path,
            'prev_story': prev_story,
            'next_story': next_story,
            **paths
        }
        
        # Render and write
        html = self.render_template('story.html', context)
        self.write_html_file(html, output_file)
        
        print(f"Generated story page: {output_file}")
    
    def generate_main_story_pages(self, activity: ActivityInfo, stories: List[Story], 
                                output_path: Path = DIST_PATH) -> None:
        """
        Generate all story pages for a main story chapter.
        
        Args:
            activity: Main story ActivityInfo object
            stories: List of story objects
            output_path: Output directory path
        """
        if not activity.zone_info:
            return
        
        chapter = activity.zone_info.chapter_number
        
        # Create stories directory
        stories_dir = output_path / 'main' / f'chapter_{chapter:02d}' / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate each story page
        for i, story in enumerate(stories):
            # Determine file name from story code
            file_name = Path(story.story_code).stem if story.story_code else f"story_{i}"
            
            # Get previous and next stories
            prev_story = None
            next_story = None
            
            if i > 0:
                prev_story_code = stories[i-1].story_code
                prev_file_name = Path(prev_story_code).stem if prev_story_code else f"story_{i-1}"
                
                prev_story = {
                    'story_name': stories[i-1].story_name,
                    'file_name': prev_file_name
                }
            
            if i < len(stories) - 1:
                next_story_code = stories[i+1].story_code
                next_file_name = Path(next_story_code).stem if next_story_code else f"story_{i+1}"
                
                next_story = {
                    'story_name': stories[i+1].story_name,
                    'file_name': next_file_name
                }
            
            # Generate story page
            self._generate_main_story_page(
                story,
                activity,
                stories_dir / f"{file_name}.html",
                output_path,
                prev_story,
                next_story
            )
    
    def _generate_main_story_page(
        self,
        story: Story,
        activity: ActivityInfo,
        output_file: Path,
        root_path: Path,
        prev_story: Optional[dict] = None,
        next_story: Optional[dict] = None
    ) -> None:
        """
        Generate a single main story page.
        
        Args:
            story: Story object
            activity: Parent activity object
            output_file: Output file path
            root_path: Root directory path
            prev_story: Previous story info
            next_story: Next story info
        """
        # Render story content
        rendered_content = render_story_content(story)
        
        # Group content by scenes
        scenes = group_dialog_by_scene(rendered_content)
        
        # Get relative paths
        paths = self.get_relative_paths(output_file, root_path)
        
        # Add chapter index path
        chapter_index_path = '../index.html'
        
        # Prepare context
        context = {
            'story': story,
            'scenes': scenes,
            'activity': activity,
            'zone_info': activity.zone_info,
            'chapter_index_path': chapter_index_path,
            'main_index_path': '../../main/index.html',
            'prev_story': prev_story,
            'next_story': next_story,
            'is_main_story': True,
            **paths
        }
        
        # Render and write
        html = self.render_template('story.html', context)
        self.write_html_file(html, output_file)
        
        print(f"Generated main story page: {output_file}")