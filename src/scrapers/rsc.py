# rsc.py

"""
RSC (Royal Shakespeare Company) Scraper

This module provides a parser for extracting show information from the Royal Shakespeare Company
What's On page. It targets the grid view within the main “whatson” article and extracts details
from each production item.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_rsc")


def extract_rsc_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from the RSC What's On page.

    The parser assumes that productions are displayed in the grid view within the main article.
    Each production is contained in a div with class "wo-grid-item" and provides:
      - Title: from the h3 element inside the title-copy container.
      - URL: from the first link with text like "BOOK TICKETS" within the performance list.
      - Venue and Date: from the "gi-info" section, where the "loc" element gives the venue and the
        "dates" element gives the performance dates.
      - Description: from the "gi-intro-copy" element.

    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier for the theater (should be "rsc").
        url: URL of the page.

    Returns:
        List of TheaterShow objects.
    """
    shows = []
    # Find the main article containing productions.
    main_article = soup.find("article", class_="whatson")
    if not main_article:
        logger.error("Could not locate the main whatson article for RSC.")
        return shows

    # Within the article, target the grid view container
    grid_view = main_article.find("div", id="grid-view")
    if not grid_view:
        logger.error("Could not find the grid view container in RSC page.")
        return shows

    # Each production is in a "wo-grid-item"
    items = grid_view.find_all("div", class_="wo-grid-item")
    logger.info(f"Found {len(items)} production items on the RSC page.")

    for item in items:
        try:
            # Title: within the header part (inside the "title-copy" container)
            title_copy = item.find("div", id="PlayTitleCopy")
            title_elem = title_copy.find("h3", class_=lambda c: c and "title" in c)
            title = title_elem.get_text(strip=True) if title_elem else "No title"

            # URL: Try to get the "BOOK TICKETS" link from the performance list ("gi-perf-list")
            perf_list = item.find("div", class_="gi-perf-list")
            ticket_link = None
            if perf_list:
                # Look for a link whose text contains "BOOK TICKETS" (case-insensitive)
                links = perf_list.find_all("a", class_=lambda c: c and "button-link" in c)
                for a in links:
                    if a.get_text(strip=True).upper().startswith("BOOK"):
                        ticket_link = a
                        break
            show_url = ticket_link.get("href", "") if ticket_link else ""
            if show_url and not show_url.startswith("http"):
                show_url = f"https://www.rsc.org.uk{show_url}"

            # Venue and Dates: in the "gi-info" section inside "gi-info-inner" and "place-time"
            gi_info = item.find("div", class_="gi-info")
            venue = ""
            dates_text = ""
            if gi_info:
                place_time = gi_info.find("div", class_="place-time")
                if place_time:
                    loc_elem = place_time.find("div", class_="loc")
                    dates_elem = place_time.find("div", class_="dates")
                    venue = loc_elem.get_text(strip=True) if loc_elem else ""
                    dates_text = dates_elem.get_text(strip=True) if dates_elem else ""
            # Attempt to parse dates from the dates_text
            start_date, end_date = None, None
            if dates_text:
                # Look for common keywords such as "From", "Until", or a range using a dash
                # Remove leading keywords like "From" or "Until"
                cleaned = re.sub(r"^(From|Until)\s+", "", dates_text, flags=re.IGNORECASE)
                parts = re.split(r"\s*[–-]\s*", cleaned)
                if len(parts) == 2:
                    start_date = parse_date_string(parts[0].strip())
                    end_date = parse_date_string(parts[1].strip())
                else:
                    start_date = parse_date_string(cleaned)

            # Description: from the "gi-intro-copy" within "gi-intro"
            gi_intro = item.find("div", class_="gi-intro")
            description = ""
            if gi_intro:
                intro_copy = gi_intro.find("div", class_="gi-intro-copy")
                description = intro_copy.get_text(" ", strip=True) if intro_copy else ""

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
            logger.info(f"Extracted RSC show: {title}")
        except Exception as e:
            logger.error(f"Error extracting RSC show: {str(e)}")
    logger.info(f"Extracted {len(shows)} shows from the RSC page.")
    return shows
