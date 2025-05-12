"""
Soho Theatre Dean Street Scraper Module

This module provides functionality to scrape show details from Soho Theatre Dean Street website.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_soho_dean")


def extract_soho_dean_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """Extract show details from the Soho Theatre Dean Street website.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier for the theater (should be "soho_dean").
        url: URL of the page.
        
    Returns:
        List of TheaterShow objects.
    """
    shows = []
    venue = "Soho Theatre Dean Street"
    
    # Soho Theatre Dean Street shows are contained in div elements with the class "card card--event"
    show_cards = soup.select("div.card.card--event")
    logger.info(f"Found {len(show_cards)} show cards on Soho Theatre Dean Street website")
    
    for card in show_cards:
        try:
            # Extract title from the card-title class
            title_elem = card.select_one(".card-title")
            if not title_elem:
                logger.warning("No title element found for Soho Theatre Dean Street show")
                continue
            title = title_elem.get_text(strip=True)
            
            # Extract URL from the a element with class "card-link"
            link_elem = card.select_one("a.card-link")
            show_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
            
            # Extract dates - usually in a span with class "date"
            date_elem = card.select_one(".date")
            
            start_date = None
            end_date = None
            
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Check if date contains a range (typically formatted like "Mon 3 - Wed 5 Mar")
                if "–" in date_text or "-" in date_text:
                    # Split by dash and process start and end dates
                    date_parts = re.split(r'[–\-]', date_text)
                    if len(date_parts) >= 2:
                        start_date_text = date_parts[0].strip()
                        end_date_text = date_parts[1].strip()
                        
                        # If end date doesn't have month/year, use from start date
                        if any(month in start_date_text for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                            month_year_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{2,4})?', start_date_text)
                            if month_year_match and not any(month in end_date_text for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                                end_date_text += " " + month_year_match.group(0)
                        
                        start_date = parse_date_string(start_date_text)
                        end_date = parse_date_string(end_date_text)
                else:
                    # Single date
                    start_date = parse_date_string(date_text)
                    end_date = start_date
            
            # Extract time if available (usually in span with class "time")
            time_elem = card.select_one(".time")
            show_time = time_elem.get_text(strip=True) if time_elem else None
            
            # Extract subtitle if available
            subtitle_elem = card.select_one(".subtitle")
            subtitle = subtitle_elem.get_text(strip=True) if subtitle_elem else None
            
            # Extract location (specific venue within Soho Theatre)
            location_elem = card.select_one(".location")
            specific_venue = location_elem.get_text(strip=True) if location_elem else ""
            
            # Extract price if available
            price_elem = card.select_one(".price")
            price_range = price_elem.get_text(strip=True) if price_elem else None
            
            # Combine subtitle with description if available
            description = subtitle
            
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
            logger.info(f"Extracted Soho Theatre Dean Street show: {title}")
        except Exception as e:
            logger.error(f"Error extracting Soho Theatre Dean Street show: {str(e)}")
    
    logger.info(f"Extracted {len(shows)} shows from Soho Theatre Dean Street")
    return shows