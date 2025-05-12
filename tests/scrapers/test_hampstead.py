# test_hampstead.py

"""
Tests for the Hampstead Theatre scraper.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.scrapers.hampstead import extract_hampstead_shows

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def read_fixture(filename):
    """Read HTML from a fixture file."""
    try:
        with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        pytest.skip(f"Fixture file {filename} not found: {e}")

@pytest.fixture
def hampstead_html():
    """Fixture for the Hampstead Theatre HTML page."""
    html = read_fixture("hampstead_actual.html")
    return html

class TestHampsteadScraper:
    """Tests for the Hampstead Theatre scraper."""

    def test_extract_hampstead_shows(self, hampstead_html):
        """Test that production items are extracted from the Hampstead Theatre page."""
        soup = BeautifulSoup(hampstead_html, "lxml")
        shows = extract_hampstead_shows(soup, "hampstead", "https://www.hampsteadtheatre.com/whats-on/main-stage/")
        assert len(shows) > 0, "Should extract at least one show from the Hampstead Theatre page"
        for show in shows:
            assert show.title, "Each show should have a title"
            assert show.url, "Each show should have a URL"
