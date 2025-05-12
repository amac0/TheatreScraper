"""
Tests for the main script.

This module tests the main script functionality, focusing on the integration
between different components.
"""

import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock, call

import pytest

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules from the main script
from main import scrape_theaters, main
from src.models import TheaterShow


@pytest.fixture
def sample_shows():
    """Create a list of sample TheaterShow objects for testing."""
    return [
        TheaterShow(
            title="Show 1",
            venue="Theatre A",
            url="https://example.com/show1",
            performance_start_date=datetime(2025, 3, 1),
            performance_end_date=datetime(2025, 3, 31),
            theater_id="theater_a",
            price_range="£20-50"
        ),
        TheaterShow(
            title="Show 2",
            venue="Theatre B",
            url="https://example.com/show2",
            performance_start_date=datetime(2025, 4, 1),
            performance_end_date=datetime(2025, 4, 30),
            theater_id="theater_b",
            description="An exciting show"
        )
    ]


@pytest.fixture
def sample_comparison_results(sample_shows):
    """Create sample comparison results for testing."""
    return {
        'new_shows': sample_shows,
        'updated_shows': [],
        'unchanged_shows': [],
        'removed_shows': []
    }


class TestMain:
    """Tests for the main script."""
    
    @patch('main.get_theater_urls')
    @patch('main.scrape_theater_shows')
    def test_scrape_theaters(self, mock_scrape, mock_get_urls):
        """Test scraping theaters with the main script."""
        # Mock the theater URLs
        mock_get_urls.return_value = {
            "theater_a": "https://example.com/theater_a",
            "theater_b": "https://example.com/theater_b"
        }
        
        # Mock the scraper function to return different shows for each theater
        def mock_scrape_side_effect(theater_id, url):
            if theater_id == "theater_a":
                return [
                    TheaterShow(title="Show A1", venue="Theatre A", url="https://example.com/a1", theater_id="theater_a"),
                    TheaterShow(title="Show A2", venue="Theatre A", url="https://example.com/a2", theater_id="theater_a")
                ]
            elif theater_id == "theater_b":
                return [
                    TheaterShow(title="Show B1", venue="Theatre B", url="https://example.com/b1", theater_id="theater_b")
                ]
            return []
        
        mock_scrape.side_effect = mock_scrape_side_effect
        
        # Call the function
        shows, errors = scrape_theaters()
        
        # Check results
        assert len(shows) == 3
        assert len(errors) == 0
        assert mock_scrape.call_count == 2
        
        # Check that we got shows from both theaters
        assert len([s for s in shows if s.theater_id == "theater_a"]) == 2
        assert len([s for s in shows if s.theater_id == "theater_b"]) == 1
    
    @patch('main.get_theater_urls')
    @patch('main.scrape_theater_shows')
    def test_scrape_theaters_with_filter(self, mock_scrape, mock_get_urls):
        """Test scraping specific theaters with a filter."""
        # Mock the theater URLs
        mock_get_urls.return_value = {
            "theater_a": "https://example.com/theater_a",
            "theater_b": "https://example.com/theater_b",
            "theater_c": "https://example.com/theater_c"
        }
        
        # Mock the scraper function to return shows for each theater
        mock_scrape.return_value = [
            TheaterShow(title="Test Show", venue="Test Theatre", url="https://example.com/test", theater_id="theater_b")
        ]
        
        # Call the function with a filter
        shows, errors = scrape_theaters(["theater_b"])
        
        # Check results
        assert len(shows) == 1
        assert len(errors) == 0
        assert mock_scrape.call_count == 1
        mock_scrape.assert_called_once_with("theater_b", "https://example.com/theater_b")
    
    @patch('main.get_theater_urls')
    @patch('main.scrape_theater_shows')
    def test_scrape_theaters_with_errors(self, mock_scrape, mock_get_urls):
        """Test handling errors when scraping theaters."""
        # Mock the theater URLs
        mock_get_urls.return_value = {
            "theater_a": "https://example.com/theater_a",
            "theater_b": "https://example.com/theater_b"
        }
        
        # Mock the scraper function to succeed for one theater and fail for another
        def mock_scrape_side_effect(theater_id, url):
            if theater_id == "theater_a":
                return [
                    TheaterShow(title="Show A", venue="Theatre A", url="https://example.com/a", theater_id="theater_a")
                ]
            elif theater_id == "theater_b":
                raise Exception("Test error")
            return []
        
        mock_scrape.side_effect = mock_scrape_side_effect
        
        # Call the function
        shows, errors = scrape_theaters()
        
        # Check results
        assert len(shows) == 1
        assert len(errors) == 1
        assert "theater_b" in errors[0]
        assert "Test error" in errors[0]
    
    @patch('main.parse_arguments')
    @patch('main.setup_logging')
    @patch('main.validate_config')
    @patch('main.scrape_theaters')
    @patch('main.generate_daily_snapshot')
    @patch('main.notify_updates')
    def test_main_integration(self, mock_notify, mock_generate, mock_scrape, 
                             mock_validate, mock_setup_logging, mock_parse_args, sample_shows, sample_comparison_results):
        """Test the main function integration."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.no_email = False
        mock_args.theaters = None
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        
        # Mock configuration validation
        mock_validate.return_value = []
        
        # Mock scraping
        mock_scrape.return_value = (sample_shows, [])
        
        # Mock snapshot generation and comparison
        mock_generate.return_value = sample_comparison_results
        
        # Mock email notification
        mock_notify.return_value = True
        
        # Call the main function
        result = main()
        
        # Check results
        assert result == 0
        mock_setup_logging.assert_called_once()
        mock_validate.assert_called_once()
        mock_scrape.assert_called_once_with(None)
        mock_generate.assert_called_once_with(sample_shows)
        mock_notify.assert_called_once_with(sample_comparison_results, [])