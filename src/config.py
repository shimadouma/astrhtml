"""Configuration module."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'ArknightsStoryJson' / 'ja_JP'  # Japanese data path
ARKNIGHTS_STORY_JSON_PATH = DATA_PATH  # Path to Japanese data
MAIN_STORY_PATH = ARKNIGHTS_STORY_JSON_PATH / 'gamedata' / 'story' / 'obt' / 'main'
TEMPLATE_PATH = PROJECT_ROOT / 'templates'
STATIC_PATH = PROJECT_ROOT / 'static'
DIST_PATH = PROJECT_ROOT / 'dist'

# Build settings
CLEAN_BUILD = True  # Clean dist directory before build
COPY_STATIC = True  # Copy static files to dist

# Content settings
MAX_EVENTS_PER_PAGE = 50
SORT_EVENTS_BY_DATE = True  # Sort events by date (newest first)
INCLUDE_REPLICATE_EVENTS = False  # Include replicate events

# Main story settings  
INCLUDE_MAIN_STORY_BY_DEFAULT = True  # Include main story in builds by default
MAX_MAIN_CHAPTERS = None  # Limit chapters to build (None = all available)
MAIN_STORY_SORT_ORDER = 'chapter_asc'  # Sort main story by chapter (ascending)

# HTML settings
DEFAULT_ENCODING = 'utf-8'
PRETTY_HTML = True  # Pretty print HTML output