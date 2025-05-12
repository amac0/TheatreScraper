#!/usr/bin/env python3
"""
London Theater Show Scraper - Main Script

This script runs the entire process of scraping theater websites,
comparing data to previous snapshots, and sending email notifications.
"""

import argparse
import os
import sys
import time
import dotenv
from datetime import datetime
from typing import Dict, List, Tuple

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.config import (
    get_theater_urls, 
    get_dynamic_websites, 
    validate_config
)
from src.logger import get_logger, setup_logging
from src.models import TheaterShow
from src.scrapers import scrape_theater_shows
from src.data_storage import generate_daily_snapshot
from src.notifier import notify_updates

# Initialize logger
logger = get_logger("main")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Scrape London theater websites for show information.")
    parser.add_argument("--no-email", action="store_true", help="Don't send email notifications")
    parser.add_argument("--theaters", nargs="+", help="Only scrape specific theaters (space-separated IDs)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def scrape_theaters(theater_ids: List[str] = None) -> Tuple[List[TheaterShow], List[str]]:
    """
    Scrape data from all configured theater websites.
    
    Args:
        theater_ids: Optional list of theater IDs to scrape. If None, scrape all configured theaters.
        
    Returns:
        Tuple containing a list of TheaterShow objects and a list of error messages
    """
    theater_urls = get_theater_urls()
    dynamic_websites = get_dynamic_websites()
    
    # If specific theaters are requested, filter the URLs
    if theater_ids:
        theater_urls = {id: url for id, url in theater_urls.items() if id in theater_ids}
        if not theater_urls:
            logger.error(f"No valid theater IDs found among: {theater_ids}")
            return [], [f"No valid theater IDs found among: {theater_ids}"]
    
    all_shows = []
    errors = []
    
    logger.info(f"Starting to scrape {len(theater_urls)} theater websites")
    
    for theater_id, url in theater_urls.items():
        start_time = time.time()
        logger.info(f"Scraping {theater_id} from {url}")
        
        try:
            # Determine whether to use static or dynamic scraper based on configuration
            # Note: In a real implementation, if dynamic_websites contains theater_id, 
            # we'd use Selenium here. For now, we'll use the static scraper for all.
            shows = scrape_theater_shows(theater_id, url)
            
            if shows:
                logger.info(f"Successfully scraped {len(shows)} shows from {theater_id}")
                all_shows.extend(shows)
            else:
                error_msg = f"No shows found on {theater_id} at {url}"
                logger.warning(error_msg)
                errors.append(error_msg)
                
        except Exception as e:
            error_msg = f"Error scraping {theater_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        # Log the time taken
        elapsed = time.time() - start_time
        logger.info(f"Finished scraping {theater_id} in {elapsed:.2f} seconds")
    
    logger.info(f"Scraped a total of {len(all_shows)} shows from {len(theater_urls)} theaters")
    return all_shows, errors


def main():
    """Main execution function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging with appropriate level
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    
    start_time = datetime.now()
    logger.info(f"London Theater Show Scraper starting at {start_time}")
    
    # Validate configuration
    config_issues = validate_config()
    if config_issues:
        for issue in config_issues:
            logger.error(f"Configuration error: {issue}")
        logger.error("Exiting due to configuration errors")
        sys.exit(1)
    
    # Scrape theater websites
    shows, errors = scrape_theaters(args.theaters)
    
    if not shows:
        logger.error("No shows were scraped. Exiting.")
        sys.exit(1)
    
    # Save data and compare with previous snapshot
    logger.info("Generating daily snapshot and comparing with previous data")
    comparison_results = generate_daily_snapshot(shows)
    
    # Log comparison results
    logger.info(f"Comparison results: {len(comparison_results['new_shows'])} new, "
                f"{len(comparison_results['updated_shows'])} updated, "
                f"{len(comparison_results['removed_shows'])} removed, "
                f"{len(comparison_results['unchanged_shows'])} unchanged")
    
    # Send email notification if not disabled
    if not args.no_email:
        logger.info("Sending email notification")
        if notify_updates(comparison_results, errors):
            logger.info("Email notification sent successfully")
        else:
            logger.error("Failed to send email notification")
    else:
        logger.info("Email notification disabled via command line argument")
    
    # Log completion summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Scraper completed at {end_time}, total time: {duration:.2f} seconds")
    
    # Print summary to console
    print(f"\nSummary of changes:")
    print(f"- New shows: {len(comparison_results['new_shows'])}")
    print(f"- Updated shows: {len(comparison_results['updated_shows'])}")
    print(f"- Removed shows: {len(comparison_results['removed_shows'])}")
    print(f"- Unchanged shows: {len(comparison_results['unchanged_shows'])}")
    print(f"- Errors: {len(errors)}")
    
    logger.info("Theater scraper completed successfully")
    return 0


if __name__ == "__main__":
    main()