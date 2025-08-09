"""Story page generator."""
from pathlib import Path
from typing import List, Optional

from .base_generator import BaseGenerator
from ..models.event import Event
from ..models.story import Story
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
        
        # Get sorted stories
        stories = event.get_sorted_stories()
        
        # Generate each story page
        for i, story in enumerate(stories):
            # Determine file name
            file_name = Path(story.story_code).stem if story.story_code else f"story_{i}"
            
            # Get previous and next stories
            prev_story = None
            next_story = None
            
            if i > 0:
                prev_story_code = stories[i-1].story_code
                prev_story = {
                    'story_name': stories[i-1].story_name,
                    'file_name': Path(prev_story_code).stem if prev_story_code else f"story_{i-1}"
                }
            
            if i < len(stories) - 1:
                next_story_code = stories[i+1].story_code
                next_story = {
                    'story_name': stories[i+1].story_name,
                    'file_name': Path(next_story_code).stem if next_story_code else f"story_{i+1}"
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