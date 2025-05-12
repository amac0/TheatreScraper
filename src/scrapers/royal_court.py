"""
Royal Court Theatre Scraper Module

This module provides functionality to scrape show details from the Royal Court Theatre website.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_royal_court")


def extract_royal_court_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """Extract show details from the Royal Court Theatre website.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier for the theater (should be "royal_court").
        url: URL of the page.
        
    Returns:
        List of TheaterShow objects.
    """
    shows = []
    venue = "Royal Court Theatre"
    
    # Shows are contained in div elements with the class "event-block"
    show_cards = soup.select("div.event-block")
    logger.info(f"Found {len(show_cards)} show cards on Royal Court Theatre website")
    
    for card in show_cards:
        try:
            # Extract title from the event-title class
            title_elem = card.select_one(".event-title")
            if not title_elem:
                logger.warning("No title element found for Royal Court Theatre show")
                continue
            title = title_elem.get_text(strip=True)
            
            # Extract URL from the a element that wraps the figure/image
            link_elem = card.find_parent("a") or card.select_one("a")
            show_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
            
            # Extract the venue location (specific venue within Royal Court)
            location_elem = card.select_one(".event-location")
            specific_venue = location_elem.get_text(strip=True) if location_elem else venue
            if not specific_venue:
                specific_venue = venue
            
            # Extract dates from the event-time element
            date_elem = card.select_one(".event-time")
            
            start_date = None
            end_date = None
            
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Check if date contains a range (typically formatted like "Fri 21 Feb - Sat 08 Mar")
                if "-" in date_text:
                    # Split by dash and process start and end dates
                    date_parts = date_text.split("-")
                    if len(date_parts) >= 2:
                        start_date_text = date_parts[0].strip()
                        end_date_text = date_parts[1].strip()
                        
                        start_date = parse_date_string(start_date_text)
                        end_date = parse_date_string(end_date_text)
                else:
                    # Single date
                    start_date = parse_date_string(date_text)
                    end_date = start_date
            
            # Extract subheading/playwright info
            subheading_elem = card.select_one(".event-subheading")
            description = subheading_elem.get_text(strip=True) if subheading_elem else None
            
            # Check for booking status
            btn_elem = card.select_one(".btn")
            status = btn_elem.get_text(strip=True) if btn_elem else "Unknown"
            
            # For sold out shows, add this info to the description
            if btn_elem and "sold-out" in btn_elem.get("class", []):
                price_range = "Sold Out"
            else:
                price_range = None
            
            show = TheaterShow(
                title=title,
                venue=specific_venue,
                url=show_url,
                performance_start_date=start_date,
                performance_end_date=end_date,
                description=description,
                price_range=price_range,
                theater_id=theater_id
            )
            shows.append(show)
            logger.info(f"Extracted Royal Court Theatre show: {title}")
        except Exception as e:
            logger.error(f"Error extracting Royal Court Theatre show: {str(e)}")
    
    logger.info(f"Extracted {len(shows)} shows from Royal Court Theatre")
    return shows