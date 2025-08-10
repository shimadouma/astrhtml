#!/usr/bin/env python3
"""Main build script for Arknights Story HTML."""
import argparse
import subprocess
import sys
from pathlib import Path

from src.config import (
    DATA_PATH, DIST_PATH, STATIC_PATH,
    CLEAN_BUILD, COPY_STATIC, SORT_EVENTS_BY_DATE,
    INCLUDE_REPLICATE_EVENTS, INCLUDE_MAIN_STORY_BY_DEFAULT
)
from src.lib.event_parser import get_events_with_stories, sort_events_by_date
from src.lib.story_parser import parse_event_stories, create_stories_from_files
from src.lib.zone_parser import load_zone_table, get_available_main_chapters, get_ordered_main_zones
from src.lib.main_story_parser import (
    scan_main_story_files, group_files_by_chapter, create_main_story_activities
)
from src.lib.stage_parser import load_stage_table
from src.generators.index_generator import IndexGenerator
from src.generators.event_generator import EventGenerator
from src.generators.story_generator import StoryGenerator
from src.generators.main_story_generator import MainStoryGenerator
from src.generators.search_index import SearchIndexGenerator
from src.generators.bookmark_generator import BookmarkGenerator
from src.utils.file_utils import clean_directory, copy_static_files


def build_site(clean: bool = CLEAN_BUILD, limit: int = None, event_id: str = None,
               include_main: bool = INCLUDE_MAIN_STORY_BY_DEFAULT, main_only: bool = False, 
               main_chapters: list = None, check_links: bool = True):
    """
    Build the entire site.
    
    Args:
        clean: Whether to clean dist directory first
        limit: Limit number of events to process (for testing)
        event_id: Build only specific event by ID
        include_main: Whether to include main story
        main_only: Whether to build only main story (skip events)
        main_chapters: List of specific chapters to build (e.g., [0, 1, 2])
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
    
    # Load events (unless main_only is True)
    events = []
    if not main_only:
        print("Loading events from data...")
        events = get_events_with_stories(DATA_PATH)
        
        if not events:
            print("No events found!")
        else:
            print(f"Found {len(events)} events with stories")
            
            # Filter out replicate events if configured
            if not INCLUDE_REPLICATE_EVENTS:
                events = [e for e in events if not e.activity_info.is_replicate]
                print(f"Filtered to {len(events)} non-replicate events")
            
            # Filter to specific event if specified
            if event_id:
                events = [e for e in events if e.event_id == event_id]
                if not events:
                    print(f"Error: Event '{event_id}' not found!")
                    return
                else:
                    print(f"Found event: {events[0].event_name}")
            else:
                # Sort events
                if SORT_EVENTS_BY_DATE:
                    events = sort_events_by_date(events, reverse=True)
                
                # Limit events if specified
                if limit:
                    events = events[:limit]
                    print(f"Processing first {limit} events")
    
    # Load main story data if requested (but not when building specific event)
    main_story_activities = []
    if (include_main or main_only) and not event_id:
        print("\nLoading main story data...")
        
        # Load zone and stage data
        zones = load_zone_table(DATA_PATH)
        stages = load_stage_table(DATA_PATH)
        
        if not zones:
            print("No zones found in zone_table.json!")
        else:
            # Get available chapters
            available_chapters = get_available_main_chapters(zones)
            print(f"Found {len(available_chapters)} main story chapters: {available_chapters}")
            
            # Filter chapters if specific ones requested
            if main_chapters:
                available_chapters = [ch for ch in available_chapters if ch in main_chapters]
                print(f"Building chapters: {available_chapters}")
            
            if available_chapters:
                # Scan story files
                main_story_path = DATA_PATH / "gamedata" / "story" / "obt" / "main"
                story_files = scan_main_story_files(main_story_path)
                print(f"Found {len(story_files)} main story files")
                
                # Create activities for available chapters
                main_story_activities = create_main_story_activities(zones, available_chapters)
                print(f"Created {len(main_story_activities)} main story activities")
    
    # Parse stories for each event
    if events:
        print("\nParsing event stories...")
        for i, event in enumerate(events, 1):
            print(f"[{i}/{len(events)}] Parsing stories for {event.event_name}")
            parse_event_stories(event)
    
    # Generate pages
    print("\nGenerating HTML pages...")
    
    # Initialize generators
    index_gen = IndexGenerator()
    event_gen = EventGenerator()
    story_gen = StoryGenerator()
    main_story_gen = MainStoryGenerator()
    search_gen = SearchIndexGenerator()
    bookmark_gen = BookmarkGenerator(output_dir=DIST_PATH)
    
    # Generate search index (for events)
    if events:
        print("Generating search index...")
        search_gen.generate(events, DIST_PATH)
    
    # Generate index page (with main story if available)
    print("Generating index page...")
    index_gen.generate(events, main_story_activities, DIST_PATH)
    
    # Generate bookmarks page
    print("Generating bookmarks page...")
    bookmark_gen.generate_bookmarks_page()
    
    # Generate event and story pages
    if events:
        for i, event in enumerate(events, 1):
            print(f"[{i}/{len(events)}] Generating pages for {event.event_name}")
            
            # Generate event page
            event_gen.generate(event, DIST_PATH)
            
            # Generate story pages
            if event.stories:
                story_gen.generate(event, DIST_PATH)
    
    # Generate main story pages
    if main_story_activities:
        print(f"\nGenerating main story pages...")
        
        # Generate main story index
        print("Generating main story index page...")
        main_story_gen.generate_main_index(main_story_activities, DIST_PATH)
        
        # Group story files by chapter for processing
        chapters_files = group_files_by_chapter(story_files)
        
        # Generate each chapter
        for activity in main_story_activities:
            chapter = activity.zone_info.chapter_number
            print(f"Generating chapter {chapter:02d}: {activity.zone_info.display_title}")
            
            # Get story files for this chapter
            chapter_story_files = chapters_files.get(chapter, [])
            
            # Generate chapter page
            main_story_gen.generate_chapter(activity, stages, chapter_story_files, DIST_PATH)
            
            # Generate individual story pages
            if chapter_story_files:
                # Create story objects from files
                story_file_paths = []
                for story_file in chapter_story_files:
                    story_path = DATA_PATH / "gamedata" / "story" / "obt" / "main" / story_file.filename
                    story_file_paths.append(story_path)
                
                stories = create_stories_from_files(story_file_paths)
                if stories:
                    print(f"  Generated {len(stories)} story pages for chapter {chapter:02d}")
                    story_gen.generate_main_story_pages(activity, stories, DIST_PATH)
    
    # Run link health check if enabled
    if check_links:
        print("\nRunning link health check...")
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_links.py", "--dist-dir", str(DIST_PATH), "--fail-on-broken"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Link health check passed: All links are working correctly!")
            else:
                print("❌ Link health check failed:")
                print(result.stdout)
                if result.stderr:
                    print("Error:", result.stderr)
                sys.exit(1)
                
        except FileNotFoundError:
            print("Warning: Link checker script not found. Skipping link check.")
        except Exception as e:
            print(f"Warning: Link check failed with error: {e}")
    
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
    parser.add_argument(
        '--include-main',
        action='store_true',
        help='Include main story in build'
    )
    parser.add_argument(
        '--main-only',
        action='store_true',
        help='Build only main story (skip events)'
    )
    parser.add_argument(
        '--main-chapters',
        type=str,
        help='Comma-separated list of specific chapters to build (e.g., "0,1,2")'
    )
    parser.add_argument(
        '--check-links',
        action='store_true',
        help='Check for broken links after build (default: enabled)'
    )
    parser.add_argument(
        '--no-check-links',
        action='store_true',
        help='Skip link checking after build'
    )
    
    args = parser.parse_args()
    
    # Parse main chapters
    main_chapters = None
    if args.main_chapters:
        try:
            main_chapters = [int(ch.strip()) for ch in args.main_chapters.split(',')]
        except ValueError:
            print("Error: --main-chapters must be comma-separated integers", file=sys.stderr)
            sys.exit(1)
    
    # Determine link checking setting
    check_links = not args.no_check_links
    
    # Build site
    try:
        build_site(
            clean=not args.no_clean,
            limit=args.limit,
            event_id=args.event,
            include_main=args.include_main if args.include_main else INCLUDE_MAIN_STORY_BY_DEFAULT,
            main_only=args.main_only,
            main_chapters=main_chapters,
            check_links=check_links
        )
    except Exception as e:
        print(f"Error during build: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()