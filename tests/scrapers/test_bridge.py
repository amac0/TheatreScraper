# test_bridge.py

"""
Tests for the Bridge Theatre scraper.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.scrapers.bridge import extract_bridge_shows

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def read_fixture(filename):
    """Read HTML from a fixture file."""
    try:
        with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        pytest.skip(f"Fixture file {filename} not found: {e}")

@pytest.fixture
def bridge_html():
    """Fixture for the Bridge Theatre HTML page."""
    html = read_fixture("bridge_actual.html")
    return html

class TestBridgeScraper:
    """Tests for the Bridge Theatre scraper."""

    def test_extract_bridge_shows(self, bridge_html):
        """Test that at least one performance is extracted from the Bridge Theatre page."""
        soup = BeautifulSoup(bridge_html, "lxml")
        shows = extract_bridge_shows(soup, "bridge", "https://bridgetheatre.co.uk/performances/")
        assert len(shows) > 0, "Should extract at least one show from the Bridge Theatre page"
        for show in shows:
            assert show.title, "Each show should have a title"
            assert show.url, "Each show should have a URL"
