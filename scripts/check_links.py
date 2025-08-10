#!/usr/bin/env python3
"""
Link health check script for the Arknights Story Archive site.
Scans all HTML files and verifies that internal links are valid.
"""

import os
import sys
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import argparse
from typing import Set, List, Tuple, Dict


def is_internal_link(href: str) -> bool:
    """Check if a link is internal to the site."""
    if not href:
        return False
    
    # Skip external URLs
    parsed = urlparse(href)
    if parsed.netloc:  # Has domain name
        return False
    
    # Skip anchors, mailto, javascript, etc.
    if href.startswith(('#', 'mailto:', 'javascript:', 'tel:', 'data:')):
        return False
    
    return True


def normalize_path(base_path: Path, href: str) -> Path:
    """Convert a relative href to an absolute file path."""
    # Remove anchor fragments
    href = href.split('#')[0]
    
    if not href:
        return base_path
    
    # Convert relative path to absolute
    if href.startswith('/'):
        # Absolute path from site root
        return Path('dist') / href.lstrip('/')
    else:
        # Relative path from current file
        return (base_path.parent / href).resolve()


def extract_links_from_html(file_path: Path) -> List[str]:
    """Extract all internal links from an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    links = []
    
    # Find all <a> tags with href attributes
    for link in soup.find_all('a', href=True):
        href = link['href']
        if is_internal_link(href):
            links.append(href)
    
    # Find all <link> tags with href attributes (CSS, etc.)
    for link in soup.find_all('link', href=True):
        href = link['href']
        if is_internal_link(href):
            links.append(href)
    
    # Find all <script> tags with src attributes
    for script in soup.find_all('script', src=True):
        src = script['src']
        if is_internal_link(src):
            links.append(src)
    
    # Find all <img> tags with src attributes
    for img in soup.find_all('img', src=True):
        src = img['src']
        if is_internal_link(src):
            links.append(src)
    
    return links


def check_file_exists(file_path: Path) -> bool:
    """Check if a file exists, handling directory index files."""
    if file_path.exists():
        return True
    
    # If path points to directory, check for index.html
    if file_path.is_dir():
        index_file = file_path / 'index.html'
        return index_file.exists()
    
    # If path has no extension and doesn't exist, try adding .html
    if not file_path.suffix and not file_path.exists():
        html_file = file_path.with_suffix('.html')
        return html_file.exists()
    
    # If path ends with /, check for index.html
    if str(file_path).endswith('/'):
        index_file = Path(str(file_path).rstrip('/')) / 'index.html'
        return index_file.exists()
    
    return False


def find_html_files(directory: Path) -> List[Path]:
    """Find all HTML files in the directory recursively."""
    html_files = []
    for file_path in directory.rglob('*.html'):
        html_files.append(file_path)
    return sorted(html_files)


def check_links_in_site(dist_dir: Path, verbose: bool = False) -> Tuple[int, int, List[Tuple[Path, str, Path]]]:
    """
    Check all links in the site.
    
    Returns:
        tuple: (total_links_checked, broken_links_count, broken_links_details)
    """
    html_files = find_html_files(dist_dir)
    broken_links = []
    total_links = 0
    
    print(f"Checking links in {len(html_files)} HTML files...")
    
    for html_file in html_files:
        if verbose:
            print(f"Checking: {html_file}")
        
        links = extract_links_from_html(html_file)
        
        for href in links:
            total_links += 1
            
            # Convert href to absolute file path
            target_path = normalize_path(html_file, href)
            
            # Check if target exists
            if not check_file_exists(target_path):
                broken_links.append((html_file, href, target_path))
                if verbose:
                    print(f"  BROKEN: {href} -> {target_path}")
            elif verbose:
                print(f"  OK: {href}")
    
    return total_links, len(broken_links), broken_links


def main():
    parser = argparse.ArgumentParser(description='Check for broken internal links in the site')
    parser.add_argument('--dist-dir', default='dist', help='Path to the dist directory (default: dist)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fail-on-broken', action='store_true', help='Exit with error code if broken links found')
    
    args = parser.parse_args()
    
    dist_dir = Path(args.dist_dir)
    
    if not dist_dir.exists():
        print(f"Error: Directory '{dist_dir}' does not exist")
        sys.exit(1)
    
    if not dist_dir.is_dir():
        print(f"Error: '{dist_dir}' is not a directory")
        sys.exit(1)
    
    print("=" * 60)
    print("Arknights Story Archive - Link Health Check")
    print("=" * 60)
    
    total_links, broken_count, broken_details = check_links_in_site(dist_dir, args.verbose)
    
    print(f"\nResults:")
    print(f"  Total links checked: {total_links}")
    print(f"  Broken links found: {broken_count}")
    
    if broken_count > 0:
        print(f"\nBroken links details:")
        print("-" * 60)
        
        # Group by file for better readability
        by_file = {}
        for html_file, href, target_path in broken_details:
            if html_file not in by_file:
                by_file[html_file] = []
            by_file[html_file].append((href, target_path))
        
        for html_file in sorted(by_file.keys()):
            print(f"\nIn file: {html_file}")
            for href, target_path in by_file[html_file]:
                print(f"  BROKEN: {href} -> {target_path}")
        
        if args.fail_on_broken:
            print(f"\nERROR: Found {broken_count} broken links")
            sys.exit(1)
    else:
        print("\n✅ All links are working correctly!")
    
    print("=" * 60)


if __name__ == '__main__':
    main()