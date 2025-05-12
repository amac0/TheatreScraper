"""
Donmar Warehouse Scraper

This module provides a parser for extracting show information from the Donmar Warehouse website.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

# Initialize logger
logger = get_logger("scraper_donmar")


def extract_donmar_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from Donmar Warehouse website.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML
        theater_id: Identifier of the theater (should be "donmar")
        url: URL of the page
        
    Returns:
        List of TheaterShow objects
    """
    shows = []
    venue = "Donmar Warehouse"
    
    # Find all show containers - updated for actual Donmar HTML structure
    show_elements = soup.select('li.eventCard')
    
    logger.info(f"Found {len(show_elements)} eventCard elements on Donmar website")
    
    for show_elem in show_elements:
        try:
            # Extract title - typically in an h2 or h3 element
            title_elem = show_elem.select_one('h2, h3, .eventCard__title')
            
            if not title_elem:
                # Try to find any element with 'title' in its class name
                title_elem = show_elem.select_one('[class*="title" i]')
            
            if not title_elem:
                # Last resort: find any heading
                title_elem = show_elem.find(['h1', 'h2', 'h3', 'h4'])
                
            if not title_elem:
                # If still no title element, skip this show
                logger.warning(f"Could not find title element for show on Donmar website")
                continue
                
            title = title_elem.get_text(strip=True)
            
            # Extract URL from the show element or title element
            link_elem = show_elem.select_one('a') or (title_elem.find('a') if hasattr(title_elem, 'find') else None)
            show_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
            
            if show_url and not show_url.startswith('http'):
                # Handle relative URLs
                if show_url.startswith('/'):
                    show_url = f"https://www.donmarwarehouse.com{show_url}"
                else:
                    show_url = f"https://www.donmarwarehouse.com/{show_url}"
            
            # Extract dates - look for elements with date information
            date_elem = show_elem.select_one('.eventCard__mainDate, .eventCard__dates, [class*="date" i]')
            date_range = date_elem.get_text(strip=True) if date_elem else ""
            
            # Extract performance dates
            start_date = None
            end_date = None
            
            if date_range:
                # Handle various date formats
                date_range = re.sub(r'\s+', ' ', date_range).strip()
                
                # Check for date ranges like "1 - 20 Mar 2023" or "1 Mar - 20 Apr 2023"
                date_parts = re.split(r'\s*[-–]\s*', date_range)
                
                if len(date_parts) == 2:
                    # Parse different date range formats
                    start_date_str = date_parts[0].strip()
                    end_date_str = date_parts[1].strip()
                    
                    # If second part doesn't have a month or year, add it from the first part
                    if re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', start_date_str, re.IGNORECASE) and not re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', end_date_str, re.IGNORECASE):
                        # Extract month (and potentially year) from first part
                        month_year_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?\b', start_date_str, re.IGNORECASE)
                        if month_year_match:
                            end_date_str = f"{end_date_str} {month_year_match.group(0)}"
                    
                    start_date = parse_date_string(start_date_str)
                    end_date = parse_date_string(end_date_str)
                else:
                    # Try to extract a single date or other date format
                    start_date = parse_date_string(date_range)
            
            # Extract description
            desc_elem = show_elem.select_one('.eventCard__description, .eventCard__snippet, [class*="description" i], [class*="snippet" i], p')
            description = None
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                # If description is too short, it might not be the actual description
                if description and len(description) < 10:
                    description = None
            
            # Try to extract price information
            price_elem = show_elem.select_one('.eventCard__price, [class*="price" i], [class*="ticket" i]')
            price_range = price_elem.get_text(strip=True) if price_elem else None
            
            # Create TheaterShow object
            show = TheaterShow(
                title=title,
                venue=venue,
                url=show_url,
                performance_start_date=start_date,
                performance_end_date=end_date,
                description=description,
                price_range=price_range,
                theater_id=theater_id
            )
            
            shows.append(show)
            logger.info(f"Extracted Donmar show: {title}")
            
        except Exception as e:
            logger.error(f"Error extracting Donmar show: {str(e)}")
    
    logger.info(f"Extracted {len(shows)} shows from Donmar Warehouse")
    return shows
