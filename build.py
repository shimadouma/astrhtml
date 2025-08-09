#!/usr/bin/env python3
"""Main build script for Arknights Story HTML."""
import argparse
import sys
from pathlib import Path

from src.config import (
    DATA_PATH, DIST_PATH, STATIC_PATH,
    CLEAN_BUILD, COPY_STATIC, SORT_EVENTS_BY_DATE,
    INCLUDE_REPLICATE_EVENTS
)
from src.lib.event_parser import get_events_with_stories, sort_events_by_date
from src.lib.story_parser import parse_event_stories
from src.generators.index_generator import IndexGenerator
from src.generators.event_generator import EventGenerator
from src.generators.story_generator import StoryGenerator
from src.utils.file_utils import clean_directory, copy_static_files


def build_site(clean: bool = CLEAN_BUILD, limit: int = None):
    """
    Build the entire site.
    
    Args:
        clean: Whether to clean dist directory first
        limit: Limit number of events to process (for testing)
    """
    print("=" * 50)
    print("Arknights Story HTML Builder")
    print("=" * 50)
    
    # Clean dist directory if requested
    if clean:
        print("Cleaning dist directory...")
        clean_directory(DIST_PATH)
    
    # Copy static files
    if COPY_STATIC:
        print("Copying static files...")
        copy_static_files(STATIC_PATH, DIST_PATH / 'static')
    
    # Load events
    print("Loading events from data...")
    events = get_events_with_stories(DATA_PATH)
    
    if not events:
        print("No events found!")
        return
    
    print(f"Found {len(events)} events with stories")
    
    # Filter out replicate events if configured
    if not INCLUDE_REPLICATE_EVENTS:
        events = [e for e in events if not e.activity_info.is_replicate]
        print(f"Filtered to {len(events)} non-replicate events")
    
    # Sort events
    if SORT_EVENTS_BY_DATE:
        events = sort_events_by_date(events, reverse=True)
    
    # Limit events if specified
    if limit:
        events = events[:limit]
        print(f"Processing first {limit} events")
    
    # Parse stories for each event
    print("\nParsing stories...")
    for i, event in enumerate(events, 1):
        print(f"[{i}/{len(events)}] Parsing stories for {event.event_name}")
        parse_event_stories(event)
    
    # Generate pages
    print("\nGenerating HTML pages...")
    
    # Initialize generators
    index_gen = IndexGenerator()
    event_gen = EventGenerator()
    story_gen = StoryGenerator()
    
    # Generate index page
    print("Generating index page...")
    index_gen.generate(events, DIST_PATH)
    
    # Generate event and story pages
    for i, event in enumerate(events, 1):
        print(f"[{i}/{len(events)}] Generating pages for {event.event_name}")
        
        # Generate event page
        event_gen.generate(event, DIST_PATH)
        
        # Generate story pages
        if event.stories:
            story_gen.generate(event, DIST_PATH)
    
    print("\n" + "=" * 50)
    print("Build complete!")
    print(f"Output directory: {DIST_PATH}")
    print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build Arknights Story HTML site'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Do not clean dist directory before build'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of events to process'
    )
    parser.add_argument(
        '--event',
        type=str,
        help='Build only specific event by ID'
    )
    
    args = parser.parse_args()
    
    # Build site
    try:
        build_site(
            clean=not args.no_clean,
            limit=args.limit
        )
    except Exception as e:
        print(f"Error during build: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()