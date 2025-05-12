# hampstead.py

"""
Hampstead Theatre Scraper

This module provides a parser for extracting show information from Hampstead Theatre’s productions page.
It targets the production list within the "m-prodlist" section.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.logger import get_logger
from src.models import TheaterShow
from src.scrapers.base import parse_date_string

logger = get_logger("scraper_hampstead")


def extract_hampstead_shows(soup: BeautifulSoup, theater_id: str, url: str) -> List[TheaterShow]:
    """
    Extract show details from the Hampstead Theatre productions page.

    The scraper locates the container with class "m-prodlist" then selects all production items 
    (each contained within a div with class "prodlist__item"). For each item, it extracts:
      - Title and URL from the h3 element with class "prodlist__title" (using the nested link).
      - Date range from the div with class "prodlist__date".
      - Billing text from the paragraph with class "prodlist__billing" (used to determine venue).
      - Description from the first paragraph inside the text block that isn’t billing or credits.
      
    If the billing text contains "DOWNSTAIRS", the venue is set to "Hampstead Downstairs"; otherwise,
    the default venue is "Hampstead Theatre".

    Args:
        soup: BeautifulSoup object of the parsed HTML.
        theater_id: Identifier of the theater (should be "hampstead").
        url: URL of the page.

    Returns:
        List of TheaterShow objects.
    """
    shows = []
    prodlist_section = soup.find("section", class_="m-prodlist")
    if not prodlist_section:
        logger.error("Could not find the production list section (m-prodlist).")
        return shows

    prod_container = prodlist_section.find("div", class_="prodlists")
    if not prod_container:
        logger.error("Could not find the productions container (prodlists).")
        return shows

    # Each production is wrapped in an element with class "prodlist__item"
    prod_items = prod_container.select("div.prodlist__item")
    logger.info(f"Found {len(prod_items)} production items on Hampstead Theatre page.")

    for item in prod_items:
        try:
            # Title and URL: from h3.prodlist__title > a
            title_elem = item.select_one("h3.prodlist__title a")
            if not title_elem:
                logger.warning("No title element found; skipping item.")
                continue
            title = title_elem.get_text(strip=True)
            show_url = title_elem.get("href", "")
            if show_url and not show_url.startswith("http"):
                show_url = f"https://www.hampsteadtheatre.com{show_url}"

            # Date range: from div.prodlist__date
            date_elem = item.find("div", class_=lambda x: x and "prodlist__date" in x)
            date_text = date_elem.get_text(strip=True) if date_elem else ""
            start_date, end_date = None, None
            if date_text:
                parts = re.split(r"\s*[–-]\s*", date_text)
                if len(parts) == 2:
                    start_date = parse_date_string(parts[0].strip())
                    end_date = parse_date_string(parts[1].strip())
                else:
                    start_date = parse_date_string(date_text)

            # Billing: from p.prodlist__billing (used for venue determination)
            billing_elem = item.find("p", class_=lambda x: x and "prodlist__billing" in x)
            billing_text = billing_elem.get_text(strip=True) if billing_elem else ""
            if "DOWNSTAIRS" in billing_text.upper():
                venue = "Hampstead Downstairs"
            else:
                venue = "Hampstead Theatre"

            # Description: choose the first <p> inside the text block that is not billing or credits.
            description = ""
            typ_container = item.find("div", class_="typ")
            if typ_container:
                for p in typ_container.find_all("p"):
                    p_class = p.get("class", [])
                    # Skip if this paragraph is billing or credits.
                    if any(cls in p_class for cls in ["prodlist__billing", "prodlist__credits"]):
                        continue
                    text = p.get_text(strip=True)
                    if text:
                        description = text
                        break

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
            logger.info(f"Extracted Hampstead show: {title}")
        except Exception as e:
            logger.error(f"Error extracting Hampstead show: {str(e)}")
    logger.info(f"Extracted {len(shows)} shows from Hampstead Theatre page.")
    return shows
