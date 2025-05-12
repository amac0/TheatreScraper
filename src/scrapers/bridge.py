# bridge.py

"""
Bridge Theatre Scraper

This module provides a parser for extracting show information from The Bridge Theatre website.
It targets the navigation overlay section (with id "global-header-overlay-block") where upcoming
performances are listed.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_bridge")


def extract_bridge_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from the Bridge Theatre website.

    The scraper locates the navigation overlay (id "global-header-overlay-block") and then selects
    all elements with the class "global-header__nav-item". For each such item, it extracts:
      - Title from the element with class "global-header__nav-heading"
      - URL from the contained <a> element with class "global-header__nav-link"
      - Date range from the element with class "global-header__nav-subheading" (which should include the dates)
    The venue is defaulted to "The Bridge Theatre".

    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier of the theater (should be "bridge").
        url: URL of the page.

    Returns:
        List of TheaterShow objects.
    """
    shows = []
    # Locate the navigation overlay container
    nav_overlay = soup.find("nav", id="global-header-overlay-block")
    if not nav_overlay:
        logger.error("Could not find the global header overlay for Bridge Theatre.")
        return shows

    # Select all performance items within the overlay
    performance_items = nav_overlay.select("div.global-header__nav-item")
    logger.info(f"Found {len(performance_items)} performance items in the Bridge Theatre navigation overlay.")

    for item in performance_items:
        try:
            link = item.find("a", class_="global-header__nav-link")
            if not link:
                continue

            # Title: from the heading element inside the link
            title_elem = link.find(class_="global-header__nav-heading")
            title = title_elem.get_text(strip=True) if title_elem else "No title"

            # URL: from the href attribute of the link
            show_url = link.get("href", "")
            if show_url and not show_url.startswith("http"):
                show_url = f"https://bridgetheatre.co.uk{show_url}"

            # Date range: from the element with class "global-header__nav-subheading date"
            date_elem = link.find("span", class_="global-header__nav-subheading")
            date_text = date_elem.get_text(strip=True) if date_elem else ""
            start_date, end_date = None, None
            if date_text:
                # Split on an en dash or hyphen
                parts = re.split(r"\s*[–-]\s*", date_text)
                if len(parts) == 2:
                    start_date = parse_date_string(parts[0].strip())
                    end_date = parse_date_string(parts[1].strip())
                else:
                    start_date = parse_date_string(date_text)

            # Use a default venue for Bridge Theatre performances
            venue = "The Bridge Theatre"

            show = TheaterShow(
                title=title,
                venue=venue,
                url=show_url,
                performance_start_date=start_date,
                performance_end_date=end_date,
                description="",
                theater_id=theater_id
            )
            shows.append(show)
            logger.info(f"Extracted Bridge Theatre show: {title}")
        except Exception as e:
            logger.error(f"Error extracting Bridge Theatre show: {str(e)}")

    logger.info(f"Extracted {len(shows)} shows from Bridge Theatre.")
    return shows
