"""
Theater Scrapers Package

This package contains scrapers for various London theaters.
Each theater has its own module with a specialized parser.
"""

from src.scrapers.base import scrape_theater_shows
from src.scrapers.donmar import extract_donmar_shows
from src.scrapers.national import extract_national_shows
from src.scrapers.bridge import extract_bridge_shows
from src.scrapers.hampstead import extract_hampstead_shows
from src.scrapers.marylebone import extract_marylebone_shows
from src.scrapers.soho_dean import extract_soho_dean_shows
from src.scrapers.soho_walthamstow import extract_soho_walthamstow_shows
from src.scrapers.rsc import extract_rsc_shows
from src.scrapers.royal_court import extract_royal_court_shows
from src.scrapers.drury_lane import extract_drury_lane_shows

# Dictionary mapping theater_id to their specific extraction functions
THEATER_PARSERS = {
    "donmar": extract_donmar_shows,
    "national": extract_national_shows,
    "bridge": extract_bridge_shows,
    "hampstead": extract_hampstead_shows,
    "marylebone": extract_marylebone_shows,
    "soho_dean": extract_soho_dean_shows,
    "soho_walthamstow": extract_soho_walthamstow_shows,
    "rsc": extract_rsc_shows,
    "royal_court": extract_royal_court_shows,
    "drury_lane": extract_drury_lane_shows
}

__all__ = [
    'scrape_theater_shows',
    'extract_donmar_shows',
    'extract_national_shows',
    'extract_bridge_shows',
    'extract_hampstead_shows',
    'extract_marylebone_shows',
    'extract_soho_dean_shows',
    'extract_soho_walthamstow_shows',
    'extract_rsc_shows',
    'extract_royal_court_shows',
    'extract_drury_lane_shows',
    'THEATER_PARSERS'
]
