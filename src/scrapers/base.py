"""
Base Scraper Module

This module provides common functionality for all theater scrapers,
including HTML fetching, date parsing, and the main scraping interface.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Callable

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from src.config import get_scraper_config
from src.logger import get_logger
from src.models import TheaterShow

# Initialize logger
logger = get_logger("scraper_base")


def fetch_html(url: str, max_retries: Optional[int] = None, 
               retry_delay: Optional[float] = None,
               timeout: Optional[int] = None,
               user_agent: Optional[str] = None) -> Optional[str]:
    """
    Fetch HTML content from a URL with retry logic.
    
    Args:
        url: The URL to fetch
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        timeout: Request timeout in seconds
        user_agent: User agent string for the HTTP request
    
    Returns:
        HTML content as string if successful, None otherwise
    """
    # Get default values from config if not specified
    config = get_scraper_config()
    max_retries = max_retries if max_retries is not None else config["max_retries"]
    retry_delay = retry_delay if retry_delay is not None else config["retry_delay"]
    timeout = timeout if timeout is not None else config["request_timeout"]
    user_agent = user_agent if user_agent is not None else config["user_agent"]
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    logger.info(f"Fetching HTML from {url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            logger.info(f"Successfully fetched HTML from {url} (status: {response.status_code})")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url} (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Maximum retry attempts reached for {url}")
                return None
    
    return None


def parse_date_string(date_string: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object using multiple methods.
    
    Args:
        date_string: String representation of a date
        
    Returns:
        datetime object if parsing is successful, None otherwise
    """
    if not date_string or not isinstance(date_string, str):
        return None
    
    # Clean up the string
    clean_string = re.sub(r'\s+', ' ', date_string).strip()
    
    # Reject strings that are too short or ambiguous
    if len(clean_string) < 5:  # Too short to be a meaningful date
        return None
    
    # Check if it's just a year
    if re.match(r'^\d{4}$', clean_string):
        return None  # Just a year is too ambiguous
    
    # Try explicit formats first
    # UK/European format: day/month/year
    if re.match(r'^\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}$', clean_string):
        try:
            # Try day first for formats like DD/MM/YYYY
            return date_parser.parse(clean_string, dayfirst=True)
        except (ValueError, TypeError):
            pass
    
    try:
        # For other formats, try dateutil parser with fuzzy matching
        # This handles formats like "June 1, 2025", "1 June 2025", etc.
        result = date_parser.parse(clean_string, fuzzy=True)
        
        # Additional validation to ensure we have a meaningful date
        # Check if the parsed date has expected parts from the original string
        
        # If month name is in the string, make sure it matches the parsed month
        month_names = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 
            'september', 'october', 'november', 'december'
        ]
        
        for i, month_name in enumerate(month_names, 1):
            if month_name in clean_string.lower():
                # If there's a month name in the string, but the parsed month doesn't match
                if i % 12 != result.month % 12:  # Handle both short and long month names
                    logger.debug(f"Month name in string doesn't match parsed month: {date_string}")
                    return None
        
        # If the original has year and it doesn't match parsed year, reject it
        year_match = re.search(r'\b(20\d{2})\b', clean_string)
        if year_match and int(year_match.group(1)) != result.year:
            logger.debug(f"Year in string doesn't match parsed year: {date_string}")
            return None
        
        return result
        
    except (ValueError, TypeError):
        logger.debug(f"Failed to parse date: {date_string}")
        return None


def extract_show_details(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from a BeautifulSoup object.
    
    This is a generic function that should be overridden with theater-specific 
    extraction functions. It returns an empty list by default.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML
        theater_id: Identifier of the theater (e.g., "donmar", "national")
        url: URL of the page
        
    Returns:
        List of TheaterShow objects
    """
    logger.warning(f"No specific parser for theater_id '{theater_id}'. Using generic parser.")
    return []


def parse_theater_page(html_content: str, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Parse the HTML content of a theater page and extract show details.
    
    Args:
        html_content: HTML content as string
        theater_id: Identifier of the theater (e.g., "donmar", "national")
        url: URL of the page
        
    Returns:
        List of TheaterShow objects
    """
    if not html_content:
        logger.error(f"No HTML content to parse for {theater_id}")
        return []
    
    logger.info(f"Parsing HTML for {theater_id}")
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Import the theater parsers dynamically to avoid circular imports
    from src.scrapers import THEATER_PARSERS
    
    # Use a theater-specific parser function if available, otherwise use the generic one
    parser_func = THEATER_PARSERS.get(theater_id, extract_show_details)
    
    return parser_func(soup, theater_id, url)


def scrape_theater_shows(theater_id: str, url: str) -> List[TheaterShow]:
    """
    Scrape theater shows from a given URL.
    
    This function combines fetching and parsing logic.
    
    Args:
        theater_id: Identifier of the theater (e.g., "donmar", "national")
        url: URL of the theater's what's on page
        
    Returns:
        List of TheaterShow objects
    """
    logger.info(f"Scraping shows for {theater_id} from {url}")
    
    # Fetch HTML content
    html_content = fetch_html(url)
    
    if not html_content:
        logger.error(f"Failed to fetch HTML for {theater_id} from {url}")
        return []
    
    # Parse HTML to extract shows
    shows = parse_theater_page(html_content, theater_id, url)
    
    logger.info(f"Scraped {len(shows)} shows from {theater_id}")
    return shows
