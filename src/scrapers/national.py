# national.py

"""
National Theatre Scraper

This module provides a parser for extracting show information from the National Theatre website,
specifically targeting the "At the South Bank" section.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_national")


def extract_national_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from the National Theatre "At the South Bank" section.

    The scraper finds the section by locating an h2 header with text matching "At the South Bank"
    (case-insensitively). It then finds the parent section that contains event cards.
    Each card is processed to extract:
      - Title from the h3 element with class "c-event-card__title"
      - URL from the <a> element with class "c-event-card__cover-link"
      - Date range from the div with class "c-event-card__daterange"
      - Venue from the div with class "c-event-card__location"
      - Description from the div with class "c-event-card__description"
      
    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier of the theater (should be "national").
        url: URL of the page.
        
    Returns:
        List of TheaterShow objects.
    """
    shows = []
    # Locate the header for the "At the South Bank" section (case-insensitive).
    header = soup.find("h2", string=lambda text: text and "at the south bank" in text.lower())
    if not header:
        logger.error("Could not find the 'At the South Bank' header.")
        return shows

    # Find the parent section that contains this header.
    section_container = header.find_parent("section")
    if not section_container:
        logger.error("Could not locate the section container for 'At the South Bank'.")
        return shows

    # Select all event cards within this section.
    event_cards = section_container.select("div.c-event-card")
    logger.info(f"Found {len(event_cards)} event cards in the 'At the South Bank' section.")

    for card in event_cards:
        try:
            # Title
            title_elem = card.select_one("h3.c-event-card__title")
            title = title_elem.get_text(strip=True) if title_elem else "No title"

            # URL (from the cover link)
            link_elem = card.select_one("a.c-event-card__cover-link")
            show_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
            if show_url and not show_url.startswith("http"):
                show_url = f"https://www.nationaltheatre.org.uk{show_url}"

            # Date range
            daterange_elem = card.select_one("div.c-event-card__daterange")
            date_range = daterange_elem.get_text(strip=True) if daterange_elem else ""
            start_date, end_date = None, None
            if date_range:
                parts = re.split(r"\s*[–-]\s*", date_range)
                if len(parts) == 2:
                    start_date = parse_date_string(parts[0].strip())
                    end_date = parse_date_string(parts[1].strip())
                else:
                    start_date = parse_date_string(date_range)

            # Description
            desc_elem = card.select_one("div.c-event-card__description")
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Venue
            venue_elem = card.select_one("div.c-event-card__location")
            venue = venue_elem.get_text(" ", strip=True) if venue_elem else "National Theatre"

            show = TheaterShow(
                title=title,
                venue=venue,
                url=show_url,
                performance_start_date=start_date,
                performance_end_date=end_date,
                description=description,
                theater_id=theater_id
            )
            shows.append(show)
            logger.info(f"Extracted show: {title}")
        except Exception as e:
            logger.error(f"Error extracting show from card: {str(e)}")

    logger.info(f"Extracted {len(shows)} shows from the 'At the South Bank' section.")
    return shows
