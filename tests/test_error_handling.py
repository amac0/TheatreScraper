"""
Error Handling Tests

This module tests the error handling capabilities of the Theatre Scraper
application, ensuring that errors are properly caught, logged, and reported.
"""

import os
import sys
from unittest.mock import patch, MagicMock, call

import pytest
import requests

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scrapers.base import fetch_html, scrape_theater_shows
from main import scrape_theaters, main


class TestErrorHandling:
    """Tests for error handling in the Theatre Scraper application."""
    
    @patch('src.scrapers.base.requests.get')
    def test_fetch_html_retries(self, mock_get):
        """Test that fetch_html retries when a request fails."""
        # First two calls raise an exception, third succeeds
        mock_get.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            requests.exceptions.RequestException("Timeout error"),
            MagicMock(status_code=200, text="<html>Success</html>", raise_for_status=MagicMock())
        ]
        
        # Call the function with custom retry settings
        html = fetch_html("https://example.com", max_retries=3, retry_delay=0.01)
        
        # Verify that get was called three times
        assert mock_get.call_count == 3
        assert html == "<html>Success</html>"
    
    @patch('src.scrapers.base.requests.get')
    def test_fetch_html_max_retries_exceeded(self, mock_get):
        """Test that fetch_html returns None when max retries are exceeded."""
        # All calls raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the function with custom retry settings
        html = fetch_html("https://example.com", max_retries=2, retry_delay=0.01)
        
        # Verify that get was called twice and returned None
        assert mock_get.call_count == 2
        assert html is None
    
    @patch('src.scrapers.base.requests.get')
    def test_fetch_html_http_error(self, mock_get):
        """Test that fetch_html handles HTTP errors correctly."""
        # Create a mock response with a 404 status
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Call the function
        html = fetch_html("https://example.com", max_retries=1, retry_delay=0.01)
        
        # Verify that get was called once and returned None
        assert mock_get.call_count == 1
        assert html is None
    
    @patch('main.get_theater_urls')
    @patch('main.scrape_theater_shows')
    def test_scrape_theaters_with_all_errors(self, mock_scrape, mock_get_urls):
        """Test that scrape_theaters handles all theaters failing."""
        # Mock the theater URLs
        mock_get_urls.return_value = {
            "theater_a": "https://example.com/theater_a",
            "theater_b": "https://example.com/theater_b"
        }
        
        # Mock the scraper to raise exceptions for all theaters
        mock_scrape.side_effect = Exception("Scraping error")
        
        # Call the function
        shows, errors = scrape_theaters()
        
        # Verify results
        assert len(shows) == 0
        assert len(errors) == 2
        assert all("Scraping error" in error for error in errors)
    
    @patch('main.parse_arguments')
    @patch('main.validate_config')
    @patch('main.scrape_theaters')
    def test_main_with_config_errors(self, mock_scrape, mock_validate, mock_parse_args):
        """Test that main exits when configuration errors are found."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        
        # Mock configuration validation to return errors
        mock_validate.return_value = ["Missing SMTP server", "Invalid email address"]
        
        # Mock scrape_theaters to not be called
        mock_scrape.return_value = ([], [])
        
        # Call main function and expect a SystemExit
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        # Verify exit code is 1 (error)
        assert excinfo.value.code == 1
        
        # Verify scrape_theaters was not called
        mock_scrape.assert_not_called()
    
    @patch('main.parse_arguments')
    @patch('main.validate_config')
    @patch('main.scrape_theaters')
    def test_main_with_no_shows(self, mock_scrape, mock_validate, mock_parse_args):
        """Test that main exits when no shows are scraped."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        
        # Mock configuration validation to return no errors
        mock_validate.return_value = []
        
        # Mock scrape_theaters to return no shows
        mock_scrape.return_value = ([], ["Error 1", "Error 2"])
        
        # Call main function and expect a SystemExit
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        # Verify exit code is 1 (error)
        assert excinfo.value.code == 1