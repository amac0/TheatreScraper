# test_national.py

"""
Tests for the National Theatre scraper targeting the "At the South Bank" section.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.scrapers.national import extract_national_shows

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def read_fixture(filename):
    """Read HTML from a fixture file."""
    try:
        with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        pytest.skip(f"Fixture file {filename} not found: {e}")

@pytest.fixture
def national_html():
    """Fixture for National Theatre HTML for the 'At the South Bank' section."""
    html = read_fixture("national_actual.html")
    return html

class TestNationalScraper:
    """Tests for the National Theatre scraper (At the South Bank section)."""

    def test_extract_national_shows(self, national_html):
        """Test that shows are extracted from the 'At the South Bank' section."""
        soup = BeautifulSoup(national_html, "lxml")
        shows = extract_national_shows(soup, "national", "https://www.nationaltheatre.org.uk/whats-on/")
        assert len(shows) > 0, "Should extract at least one show from the 'At the South Bank' section"
        # Verify that each extracted show has a title and other basic fields.
        for show in shows:
            assert show.title, "Each show should have a title"
            # Venue, URL, description, and dates may be optional depending on the content.
