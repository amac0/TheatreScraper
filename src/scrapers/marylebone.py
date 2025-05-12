import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_marylebone")

def extract_marylebone_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """Extract show details from the Marylebone Theatre website.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier for the theater (should be "marylebone").
        url: URL of the page.
        
    Returns:
        List of TheaterShow objects.
    """
    shows = []
    venue = "Marylebone Theatre"

    # Marylebone productions are contained in div elements with the class "production-item"
    production_items = soup.select("div.production-item")
    logger.info(f"Found {len(production_items)} production-item elements on Marylebone website")

    for item in production_items:
        try:
            # Extract title from within the production-info container; usually in an h2 with class "show-title"
            title_elem = item.select_one(".production-info .show-title")
            if not title_elem:
                title_elem = item.find(["h1", "h2", "h3", "h4"])
            if not title_elem:
                logger.warning("No title element found for Marylebone production")
                continue
            title = title_elem.get_text(strip=True)
            
            # Extract the URL from the production-image link
            link_elem = item.select_one("a.production-image")
            show_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
            if show_url and not show_url.startswith("http"):
                # Handle relative URLs
                if show_url.startswith("/"):
                    show_url = f"https://www.marylebonetheatre.com{show_url}"
                else:
                    show_url = f"https://www.marylebonetheatre.com/{show_url}"
            
            # Extract performance dates – look for the flex-horizontal container with two divs having class "date blue"
            date_divs = item.select(".production-info .flex-horizontal .date.blue")
            start_date = None
            end_date = None
            if date_divs:
                if len(date_divs) >= 1:
                    start_date_text = date_divs[0].get_text(strip=True)
                    start_date = parse_date_string(start_date_text)
                if len(date_divs) >= 2:
                    end_date_text = date_divs[1].get_text(strip=True)
                    end_date = parse_date_string(end_date_text)
            # If only one date is present, assume it's the start date
            if not start_date and end_date:
                start_date = end_date
            
            # Extract description from the creatives block
            desc_elem = item.select_one(".production-info .creatives")
            description = desc_elem.get_text(strip=True) if desc_elem else None
            if description and len(description) < 10:
                description = None
            
            # Optionally, try to extract any price info if present
            price_elem = item.select_one(".production-info [class*='price'], [class*='ticket']")
            price_range = price_elem.get_text(strip=True) if price_elem else None
            
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
            logger.info(f"Extracted Marylebone show: {title}")
        except Exception as e:
            logger.error(f"Error extracting Marylebone show: {str(e)}")

    logger.info(f"Extracted {len(shows)} shows from Marylebone Theatre")
    return shows
