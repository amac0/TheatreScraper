import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

# Initialize logger
logger = get_logger("scraper_drury_lane")

def extract_drury_lane_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from the Theatre Royal Drury Lane website.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML
        theater_id: Identifier of the theater (should be "drury_lane")
        url: URL of the page
        
    Returns:
        List of TheaterShow objects
    """
    shows = []
    venue = "Theatre Royal Drury Lane"
    
    # Find all show containers
    show_elements = soup.select('.c-event-card__content')
    
    logger.info(f"Found {len(show_elements)} c-event-card__content elements on Drury Lane website")
    
    for show_elem in show_elements:
        try:
            # Extract title
            title_elem = show_elem.select_one('.c-event-card__title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Show"
            
            # Extract URL from the parent <a> tag
            link_elem = show_elem.find_parent("a")
            show_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
            if show_url and not show_url.startswith('http'):
                show_url = f"https://lwtheatres.co.uk{show_url}"
            
            # Extract date range
            date_elem = show_elem.select_one('.c-event-card__datetime')
            date_range = date_elem.get_text(strip=True) if date_elem else ""
            
            # Extract performance dates
            start_date = None
            end_date = None
            if date_range:
                date_parts = re.split(r'\s*[-–]\s*', date_range)
                if len(date_parts) == 2:
                    start_date = parse_date_string(date_parts[0])
                    end_date = parse_date_string(date_parts[1])
                else:
                    start_date = parse_date_string(date_range)
            
            # Extract venue
            venue_elem = show_elem.select_one('.c-event-card__venue')
            venue = venue_elem.get_text(strip=True) if venue_elem else "Theatre Royal Drury Lane"
            
            # Extract description (Not present, fallback to None)
            description = None
            
            # Extract price (Not found in HTML, fallback to None)
            price_range = None
            
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
            logger.info(f"Extracted Drury Lane show: {title}")
            
        except Exception as e:
            logger.error(f"Error extracting Drury Lane show: {str(e)}")
    
    logger.info(f"Extracted {len(shows)} shows from Theatre Royal Drury Lane")
    return shows
