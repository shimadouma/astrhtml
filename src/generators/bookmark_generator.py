"""
Bookmark page generator for Arknights Story Archive
Generates a static HTML page for bookmark management
"""

from pathlib import Path
from typing import Dict, Any
from .base_generator import BaseGenerator
from ..config import TEMPLATE_PATH


class BookmarkGenerator(BaseGenerator):
    """Generator for bookmark management page"""
    
    def __init__(self, output_dir: Path, static_base_url: str = "static/", template_dir: Path = TEMPLATE_PATH):
        super().__init__(template_dir)
        self.output_dir = output_dir
        self.static_base_url = static_base_url
    
    def generate_bookmarks_page(self) -> bool:
        """Generate the bookmarks page"""
        try:
            # Prepare template context
            context = {
                **self.get_base_context(),
                'page_type': 'bookmarks'
            }
            
            # Render template
            template = self.env.get_template('bookmarks.html')
            html_content = template.render(context)
            
            # Write to file
            output_file = self.output_dir / 'bookmarks.html'
            output_file.write_text(html_content, encoding='utf-8')
            
            print(f"Generated bookmarks page: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error generating bookmarks page: {e}")
            return False
    
    def get_base_context(self) -> Dict[str, Any]:
        """Get base template context for bookmarks page"""
        return {
            **super().get_build_context(),
            'css_path': self.static_base_url + 'css/',
            'js_path': self.static_base_url + 'js/',
            'index_path': './index.html',
            'root_path': './'
        }