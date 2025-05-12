# test_rsc.py

"""
Tests for the RSC scraper.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.scrapers.rsc import extract_rsc_shows

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def read_fixture(filename):
    """Read HTML from a fixture file."""
    try:
        with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        pytest.skip(f"Fixture file {filename} not found: {e}")

@pytest.fixture
def rsc_html():
    """Fixture for the RSC What's On page HTML."""
    html = read_fixture("rsc_actual.html")
    return html

class TestRscScraper:
    """Tests for the RSC scraper."""

    def test_extract_rsc_shows(self, rsc_html):
        """Test that production items are extracted from the RSC What's On page."""
        soup = BeautifulSoup(rsc_html, "lxml")
        shows = extract_rsc_shows(soup, "rsc", "https://www.rsc.org.uk/whats-on")
        assert len(shows) > 0, "Should extract at least one show from the RSC page"
        for show in shows:
            assert show.title, "Each show should have a title"
            # URL, venue and dates might be optional depending on the data available.
