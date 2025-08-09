"""Text processing utilities."""
import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean text for display.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ''
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def process_dialog_text(text: str) -> str:
    """
    Process dialog text for HTML display.
    
    Args:
        text: Dialog text
        
    Returns:
        Processed text
    """
    text = clean_text(text)
    
    # Convert line breaks
    text = text.replace('\\n', '<br>')
    
    # Handle special formatting tags if any
    # (Add more processing as needed based on actual data)
    
    return text


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Raw text
        
    Returns:
        HTML-escaped text
    """
    if not text:
        return ''
    
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_story_code(story_code: str) -> str:
    """
    Format story code for display.
    
    Args:
        story_code: Raw story code
        
    Returns:
        Formatted story code
    """
    if not story_code:
        return ''
    
    # Remove common prefixes
    code = story_code.replace('level_', '').replace('act', '')
    
    # Convert underscores to spaces
    code = code.replace('_', ' ')
    
    # Capitalize
    code = code.upper()
    
    return code.strip()