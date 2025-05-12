"""
Integration Tests for the Theatre Scraper Application

This module contains integration tests that simulate a full run of the
application, including scraping, data storage, and notification generation.
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import scrape_theaters, main
from src.models import TheaterShow
from src.data_storage import save_snapshot, compare_snapshots
from src.notifier import compose_email


class TestIntegration:
    """Integration tests for the Theatre Scraper application."""
    
    @pytest.fixture
    def today_shows(self):
        """Create a list of sample TheaterShow objects for today's data."""
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
            ),
            TheaterShow(
                title="Show 3",
                venue="Theatre C",
                url="https://example.com/show3",
                performance_start_date=datetime(2025, 5, 1),
                performance_end_date=datetime(2025, 5, 31),
                theater_id="theater_c",
                price_range="£15-40"
            )
        ]
    
    @pytest.fixture
    def previous_shows(self):
        """Create a list of sample TheaterShow objects for previous data with some differences."""
        return [
            TheaterShow(
                title="Show 1",
                venue="Theatre A",
                url="https://example.com/show1",
                performance_start_date=datetime(2025, 3, 10),  # Changed
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
                description="An exciting show"  # Unchanged
            ),
            # Show 3 is missing (will be detected as new)
            TheaterShow(
                title="Show 4",  # This one is removed in today's data
                venue="Theatre D",
                url="https://example.com/show4",
                performance_start_date=datetime(2025, 6, 1),
                performance_end_date=datetime(2025, 6, 30),
                theater_id="theater_d",
                price_range="£25-60"
            )
        ]
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test snapshots."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @patch('src.data_storage.get_storage_config')
    def test_data_storage_integration(self, mock_get_storage_config, today_shows, previous_shows, temp_dir):
        """Test integration between data storage components."""
        # Configure mock
        mock_get_storage_config.return_value = {"snapshots_dir": temp_dir}
        
        # Save previous snapshot
        previous_snapshot_path = save_snapshot(previous_shows, "previous_snapshot.csv")
        
        # Verify the snapshot was saved correctly
        assert os.path.exists(previous_snapshot_path)
        
        # Save today's snapshot
        today_snapshot_path = save_snapshot(today_shows, "today_snapshot.csv")
        
        # Verify today's snapshot was saved correctly
        assert os.path.exists(today_snapshot_path)
        
        # Load both snapshots with pandas and verify their content
        previous_df = pd.read_csv(previous_snapshot_path)
        today_df = pd.read_csv(today_snapshot_path)
        
        assert len(previous_df) == len(previous_shows)
        assert len(today_df) == len(today_shows)
        
        # Compare snapshots
        comparison_results = compare_snapshots(today_shows, previous_shows)
        
        # Verify comparison results
        assert len(comparison_results["new_shows"]) == 1
        assert comparison_results["new_shows"][0].title == "Show 3"
        
        assert len(comparison_results["updated_shows"]) == 1
        assert comparison_results["updated_shows"][0]["current"].title == "Show 1"
        
        assert len(comparison_results["unchanged_shows"]) == 1
        assert comparison_results["unchanged_shows"][0].title == "Show 2"
        
        assert len(comparison_results["removed_shows"]) == 1
        assert comparison_results["removed_shows"][0].title == "Show 4"
    
    def test_notification_integration(self, today_shows, previous_shows):
        """Test integration between data comparison and notification components."""
        # Compare snapshots
        comparison_results = compare_snapshots(today_shows, previous_shows)
        
        # Add some sample errors
        errors = ["Error 1: Failed to scrape Theatre X", "Error 2: Connection timeout for Theatre Y"]
        
        # Compose email notification
        email_content = compose_email(comparison_results, errors)
        
        # Verify email content
        assert "London Theater Updates" in email_content["subject"]
        assert "# London Theater Updates" in email_content["body"]
        
        # Check that the email contains all the relevant sections
        assert "## New Shows (1)" in email_content["body"]
        assert "Show 3" in email_content["body"]
        
        assert "## Updated Shows (1)" in email_content["body"]
        assert "Show 1" in email_content["body"]
        
        assert "## Unchanged Shows (1)" in email_content["body"]
        assert "Show 2" in email_content["body"]
        
        assert "## Removed Shows (1)" in email_content["body"]
        assert "Show 4" in email_content["body"]
        
        assert "## Errors Encountered (2)" in email_content["body"]
        assert "Error 1" in email_content["body"]
        assert "Error 2" in email_content["body"]
    
    @patch('main.get_theater_urls')
    @patch('main.scrape_theater_shows')
    @patch('main.generate_daily_snapshot')
    @patch('main.notify_updates')
    @patch('main.parse_arguments')
    @patch('main.setup_logging')
    def test_end_to_end_workflow(self, mock_setup_logging, mock_parse_args, mock_notify, 
                                mock_generate, mock_scrape, mock_urls, today_shows):
        """Test the end-to-end application workflow with mocks."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.no_email = False
        mock_args.theaters = None
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        
        # Mock theater URLs
        mock_urls.return_value = {
            "theater_a": "https://example.com/theater_a",
            "theater_b": "https://example.com/theater_b",
            "theater_c": "https://example.com/theater_c"
        }
        
        # Mock scraper to return our sample shows
        mock_scrape.return_value = today_shows
        
        # Mock data comparison to return a sample result
        comparison_results = {
            "new_shows": [today_shows[2]],
            "updated_shows": [],
            "unchanged_shows": [today_shows[0], today_shows[1]],
            "removed_shows": []
        }
        mock_generate.return_value = comparison_results
        
        # Mock notification to return success
        mock_notify.return_value = True
        
        # Run the main function
        exit_code = main()
        
        # Verify the workflow executed correctly
        assert exit_code == 0
        mock_setup_logging.assert_called_once()
        mock_urls.assert_called_once()
        assert mock_scrape.call_count == 3  # Called for each theater
        mock_generate.assert_called_once()
        mock_notify.assert_called_once_with(comparison_results, [])