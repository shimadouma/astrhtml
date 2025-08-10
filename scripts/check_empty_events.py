#!/usr/bin/env python3
"""
Script to check for event pages that contain no stories.
This helps identify issues with story generation or data processing.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
import re
from bs4 import BeautifulSoup

def find_event_directories(dist_path: Path) -> List[Path]:
    """Find all event directories in the dist folder."""
    events_dir = dist_path / 'events'
    if not events_dir.exists():
        return []
    
    event_dirs = []
    for item in events_dir.iterdir():
        if item.is_dir():
            event_dirs.append(item)
    
    return sorted(event_dirs)

def check_event_has_stories(event_dir: Path) -> Tuple[bool, List[str], Dict]:
    """
    Check if an event directory has stories and if they're properly linked.
    
    Returns:
        - has_stories: Boolean indicating if stories exist AND are linked
        - story_files: List of story file names found
        - event_info: Dictionary with event information
    """
    stories_dir = event_dir / 'stories'
    index_file = event_dir / 'index.html'
    
    event_info = {
        'event_id': event_dir.name,
        'has_index': index_file.exists(),
        'has_stories_dir': stories_dir.exists(),
        'story_count': 0,
        'event_title': 'Unknown',
        'stories_in_index': 0,
        'linked_stories': [],
        'unlinked_stories': [],
        'broken_links': [],
        'link_mismatch': False
    }
    
    story_files = []
    
    # Check for stories directory and get actual story files
    if stories_dir.exists():
        story_files = [f.name for f in stories_dir.iterdir() if f.is_file() and f.suffix == '.html']
        event_info['story_count'] = len(story_files)
    
    # Extract event title and check story links from index.html
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    event_info['event_title'] = title_tag.get_text().split(' - ')[0]
                
                # Check for stories listed in the index page
                story_links = soup.find_all('a', href=re.compile(r'stories/.*\.html'))
                event_info['stories_in_index'] = len(story_links)
                
                # Extract linked story file names
                linked_story_files = set()
                for link in story_links:
                    href = link.get('href')
                    if href.startswith('stories/'):
                        story_filename = href.replace('stories/', '')
                        linked_story_files.add(story_filename)
                        
                        # Check if the linked file actually exists
                        story_file_path = stories_dir / story_filename
                        if not story_file_path.exists():
                            event_info['broken_links'].append(story_filename)
                
                event_info['linked_stories'] = sorted(list(linked_story_files))
                
                # Find unlinked stories (exist as files but not linked in index)
                actual_story_files = set(story_files)
                event_info['unlinked_stories'] = sorted(list(actual_story_files - linked_story_files))
                
                # Check for link mismatch
                event_info['link_mismatch'] = len(event_info['unlinked_stories']) > 0 or len(event_info['broken_links']) > 0
                
        except Exception as e:
            print(f"Warning: Could not parse {index_file}: {e}")
            event_info['stories_in_index'] = -1
    
    # Consider event to have stories only if:
    # 1. Story files exist AND
    # 2. They are properly linked in the index page
    has_stories = len(story_files) > 0 and event_info['stories_in_index'] > 0 and not event_info['link_mismatch']
    
    return has_stories, story_files, event_info

def main():
    """Main function to check for empty event pages."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    dist_path = project_root / 'dist'
    
    if not dist_path.exists():
        print("Error: dist/ directory not found. Please run 'python build.py' first.")
        sys.exit(1)
    
    print("Checking for event pages with no stories...\n")
    
    # Find all event directories
    event_dirs = find_event_directories(dist_path)
    
    if not event_dirs:
        print("No event directories found in dist/events/")
        sys.exit(0)
    
    problematic_events = []
    total_events = len(event_dirs)
    events_with_proper_stories = 0
    events_with_link_issues = 0
    
    print(f"Found {total_events} event directories to check:\n")
    
    for event_dir in event_dirs:
        has_stories, story_files, event_info = check_event_has_stories(event_dir)
        
        # Check for various issues
        has_link_issues = event_info['link_mismatch'] or len(event_info['broken_links']) > 0
        
        if not has_stories or has_link_issues:
            problematic_events.append(event_info)
            
            # Determine the type of issue
            if len(story_files) == 0:
                print(f"❌ {event_info['event_id']} - '{event_info['event_title']}' (NO STORY FILES)")
            elif event_info['stories_in_index'] == 0:
                print(f"❌ {event_info['event_id']} - '{event_info['event_title']}' (FILES EXIST BUT NOT LINKED)")
            elif len(event_info['unlinked_stories']) > 0:
                print(f"⚠️  {event_info['event_id']} - '{event_info['event_title']}' (SOME STORIES NOT LINKED)")
            elif len(event_info['broken_links']) > 0:
                print(f"❌ {event_info['event_id']} - '{event_info['event_title']}' (BROKEN LINKS)")
            
            # Show detailed information
            print(f"   Story files on disk: {len(story_files)}")
            print(f"   Stories linked in index: {event_info['stories_in_index']}")
            if event_info['unlinked_stories']:
                print(f"   Unlinked stories: {', '.join(event_info['unlinked_stories'])}")
            if event_info['broken_links']:
                print(f"   Broken links: {', '.join(event_info['broken_links'])}")
            print()
            
            if has_link_issues and len(story_files) > 0:
                events_with_link_issues += 1
        else:
            events_with_proper_stories += 1
            print(f"✅ {event_info['event_id']} - '{event_info['event_title']}' ({len(story_files)} stories)")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total events checked: {total_events}")
    print(f"Events with proper stories: {events_with_proper_stories}")
    print(f"Events with link issues: {events_with_link_issues}")
    print(f"Events with problems: {len(problematic_events)}")
    
    if problematic_events:
        # Categorize problems
        no_files = [e for e in problematic_events if e['story_count'] == 0]
        not_linked = [e for e in problematic_events if e['story_count'] > 0 and e['stories_in_index'] == 0]
        partially_linked = [e for e in problematic_events if len(e['unlinked_stories']) > 0 and e['stories_in_index'] > 0]
        broken_links = [e for e in problematic_events if len(e['broken_links']) > 0]
        
        if no_files:
            print(f"\n{'='*60}")
            print(f"EVENTS WITH NO STORY FILES ({len(no_files)} total)")
            print(f"{'='*60}")
            for event_info in no_files:
                print(f"• {event_info['event_id']} - {event_info['event_title']}")
        
        if not_linked:
            print(f"\n{'='*60}")
            print(f"EVENTS WITH STORY FILES BUT NO LINKS ({len(not_linked)} total)")
            print(f"{'='*60}")
            for event_info in not_linked:
                print(f"• {event_info['event_id']} - {event_info['event_title']} ({event_info['story_count']} files not linked)")
        
        if partially_linked:
            print(f"\n{'='*60}")
            print(f"EVENTS WITH SOME UNLINKED STORIES ({len(partially_linked)} total)")
            print(f"{'='*60}")
            for event_info in partially_linked:
                print(f"• {event_info['event_id']} - {event_info['event_title']} ({len(event_info['unlinked_stories'])} unlinked)")
        
        if broken_links:
            print(f"\n{'='*60}")
            print(f"EVENTS WITH BROKEN LINKS ({len(broken_links)} total)")
            print(f"{'='*60}")
            for event_info in broken_links:
                print(f"• {event_info['event_id']} - {event_info['event_title']} ({len(event_info['broken_links'])} broken)")
        
        print(f"\n{'='*60}")
        print(f"TROUBLESHOOTING RECOMMENDATIONS")
        print(f"{'='*60}")
        if no_files:
            print("For events with no story files:")
            print("1. Check if story data exists in ArknightsStoryJson")
            print("2. Verify story file processing logic")
            print("3. Check for MINISTORY events (may need special handling)")
            print("4. Verify stage_table.json mappings")
            print()
        if not_linked or partially_linked:
            print("For events with unlinking issues:")
            print("1. Check event page generation logic")
            print("2. Verify template rendering for story lists")
            print("3. Check if story order determination is working")
            print("4. Verify event_generator.py story linking code")
            print()
        if broken_links:
            print("For events with broken links:")
            print("1. Check story filename generation logic")
            print("2. Verify file naming consistency")
            print("3. Check for special characters in filenames")
        
        sys.exit(1)
    else:
        print("\n🎉 All events have properly linked stories!")
        sys.exit(0)

if __name__ == '__main__':
    main()