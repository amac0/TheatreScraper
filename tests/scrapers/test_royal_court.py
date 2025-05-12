"""
Tests for the Royal Court Theatre scraper module.
"""

import os
import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from src.scrapers.royal_court import extract_royal_court_shows


@pytest.fixture
def royal_court_html():
    """Load the Royal Court Theatre sample HTML file."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "fixtures",
        "royal_court_actual.html"
    )
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()


def test_extract_royal_court_shows(royal_court_html):
    """Test extracting shows from Royal Court Theatre HTML."""
    # Parse the HTML
    soup = BeautifulSoup(royal_court_html, 'lxml')
    
    # Extract shows
    shows = extract_royal_court_shows(soup, "royal_court", "https://royalcourttheatre.com/whats-on/")
    
    # Check if shows were extracted
    assert len(shows) > 0, "No shows were extracted"
    
    # Check if all shows have the required attributes
    for show in shows:
        assert show.title, "Show title is missing"
        assert show.venue, "Show venue is missing"
        assert show.url, "Show URL is missing"
        assert show.theater_id == "royal_court", "Theater ID is incorrect"
        
        # Check at least some dates were extracted
        has_dates = False
        if show.performance_start_date or show.performance_end_date:
            has_dates = True
            
        assert has_dates, f"Show '{show.title}' has no dates"
    
    # Validate specific shows from the fixture
    # Look for shows like "More Life" and "A Knock on the Roof" that should be in the sample
    more_life_shows = [s for s in shows if "More Life" in s.title]
    assert len(more_life_shows) > 0, "More Life show not found"
    
    knock_on_roof_shows = [s for s in shows if "A Knock on the Roof" in s.title]
    assert len(knock_on_roof_shows) > 0, "A Knock on the Roof show not found"
    
    # Verify specific venue information
    jerwood_downstairs_shows = [s for s in shows if "Jerwood Theatre Downstairs" in s.venue]
    assert len(jerwood_downstairs_shows) > 0, "No shows at Jerwood Theatre Downstairs"
    
    jerwood_upstairs_shows = [s for s in shows if "Jerwood Theatre Upstairs" in s.venue]
    assert len(jerwood_upstairs_shows) > 0, "No shows at Jerwood Theatre Upstairs"
    
    # Check date parsing - exact dates will depend on the test fixture
    for show in shows:
        if show.performance_start_date:
            assert isinstance(show.performance_start_date, datetime), "Start date is not a datetime object"
        
        if show.performance_end_date:
            assert isinstance(show.performance_end_date, datetime), "End date is not a datetime object"