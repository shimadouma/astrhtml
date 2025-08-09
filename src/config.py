"""Configuration module."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'ArknightsStoryJson'
ARKNIGHTS_STORY_JSON_PATH = DATA_PATH / 'ja_JP'  # Path to Japanese data
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

# HTML settings
DEFAULT_ENCODING = 'utf-8'
PRETTY_HTML = True  # Pretty print HTML output