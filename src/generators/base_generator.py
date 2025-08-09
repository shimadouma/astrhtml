"""Base generator class."""
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from ..config import TEMPLATE_PATH, DEFAULT_ENCODING
from ..utils.file_utils import write_html, ensure_directory


class BaseGenerator:
    """Base class for HTML generators."""
    
    def __init__(self, template_dir: Path = TEMPLATE_PATH):
        """
        Initialize generator with Jinja2 environment.
        
        Args:
            template_dir: Path to templates directory
        """
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template file
            context: Template context dictionary
            
        Returns:
            Rendered HTML string
        """
        # Add build context to all templates
        full_context = {**context, **self.get_build_context()}
        
        template = self.env.get_template(template_name)
        return template.render(**full_context)
    
    def write_html_file(self, content: str, output_path: Path) -> None:
        """
        Write HTML content to file.
        
        Args:
            content: HTML content
            output_path: Output file path
        """
        write_html(content, output_path)
    
    def get_relative_paths(self, current_path: Path, root_path: Path) -> Dict[str, str]:
        """
        Get relative paths for navigation.
        
        Args:
            current_path: Current file path
            root_path: Root directory path
            
        Returns:
            Dictionary of relative paths
        """
        # Calculate depth from root
        depth = len(current_path.parent.relative_to(root_path).parts)
        
        # Build relative paths
        relative_root = '../' * depth if depth > 0 else './'
        
        return {
            'index_path': f"{relative_root}index.html",
            'css_path': f"{relative_root}static/css/",
            'js_path': f"{relative_root}static/js/",
            'root_path': relative_root
        }
    
    def get_build_context(self) -> Dict[str, Any]:
        """
        Get build-specific context variables.
        
        Returns:
            Dictionary with build information
        """
        return {
            'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }