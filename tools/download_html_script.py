#!/usr/bin/env python3
"""
HTML Downloader for Theater Websites

This script downloads HTML content from theater websites and saves it to the fixtures directory
for use in testing the scrapers.

Usage:
    python download_html.py [--all]
    python download_html.py [theater_ids...]

Examples:
    python download_html.py --all
    python download_html.py donmar national bridge
"""

import os
import sys
import argparse
import requests
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import get_theater_urls, get_scraper_config

# Configure target directory
FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"


def download_html(theater_id, url, output_path):
    """
    Download HTML content from a URL and save it to a file.
    
    Args:
        theater_id: Identifier of the theater
        url: URL to download from
        output_path: Path to save the HTML content to
    
    Returns:
        bool: True if successful, False otherwise
    """
    config = get_scraper_config()
    user_agent = config["user_agent"]
    timeout = config["request_timeout"]
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    print(f"Downloading {theater_id} HTML from {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Save the HTML content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Successfully saved {theater_id} HTML to {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {theater_id} HTML: {str(e)}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download HTML from theater websites for testing")
    parser.add_argument('--all', action='store_true', help='Download HTML from all theaters')
    parser.add_argument('theater_ids', nargs='*', help='IDs of theaters to download HTML from')
    
    args = parser.parse_args()
    
    # Ensure fixtures directory exists
    FIXTURES_DIR.mkdir(exist_ok=True, parents=True)
    
    # Get theater URLs from config
    theater_urls = get_theater_urls()
    
    # Determine which theaters to download
    theaters_to_download = []
    if args.all:
        theaters_to_download = list(theater_urls.keys())
    elif args.theater_ids:
        for theater_id in args.theater_ids:
            if theater_id in theater_urls:
                theaters_to_download.append(theater_id)
            else:
                print(f"Unknown theater ID: {theater_id}")
                print(f"Available theater IDs: {', '.join(theater_urls.keys())}")
    else:
        parser.print_help()
        sys.exit(1)
    
    # Download HTML for each theater
    success_count = 0
    for theater_id in theaters_to_download:
        url = theater_urls[theater_id]
        output_path = FIXTURES_DIR / f"{theater_id}_actual.html"
        
        if download_html(theater_id, url, output_path):
            success_count += 1
        
        # Pause between downloads to avoid overwhelming the servers
        if theater_id != theaters_to_download[-1]:
            time.sleep(1)
    
    print(f"\nDownloaded HTML for {success_count} out of {len(theaters_to_download)} theaters")
    
    if success_count > 0:
        print("\nNext steps:")
        print("1. Run the HTML analyzer to examine the structure:")
        print(f"   python tools/analyze_html.py tests/fixtures/{theaters_to_download[0]}_actual.html")
        print("2. Update the parsers if needed")
        print("3. Run the tests:")
        print("   python -m pytest tests/test_scraper_static.py -v")


if __name__ == "__main__":
    main()
