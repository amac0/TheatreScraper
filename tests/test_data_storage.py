"""
Tests for the Data Storage Module

This module tests the functionality for saving, loading, and
comparing theater show data as CSV snapshots.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.data_storage import (
    save_snapshot, 
    load_snapshot, 
    get_latest_snapshot, 
    compare_snapshots,
    generate_daily_snapshot
)
from src.models import TheaterShow


@pytest.fixture
def mock_config():
    """Create a mock storage configuration with a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    return {"snapshots_dir": temp_dir}


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
def modified_shows():
    """Create a list of modified TheaterShow objects for comparison testing."""
    return [
        TheaterShow(
            title="Show 1",
            venue="Theatre A",
            url="https://example.com/show1",
            performance_start_date=datetime(2025, 3, 10),  # Changed date
            performance_end_date=datetime(2025, 3, 31),
            theater_id="theater_a",
            price_range="£30-60"  # Changed price
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
            title="Show 3",  # New show
            venue="Theatre C",
            url="https://example.com/show3",
            performance_start_date=datetime(2025, 5, 1),
            performance_end_date=datetime(2025, 5, 31),
            theater_id="theater_c"
        )
    ]


class TestDataStorage:
    """Tests for the data storage module."""

    @patch("src.data_storage.get_storage_config")
    def test_save_snapshot(self, mock_get_storage_config, mock_config, sample_shows):
        """Test saving a snapshot to a CSV file."""
        mock_get_storage_config.return_value = mock_config
        
        # Save snapshot
        file_path = save_snapshot(sample_shows, "test_snapshot.csv")
        
        # Check that the file was created
        assert os.path.exists(file_path)
        
        # Load the CSV with pandas and check its content
        df = pd.read_csv(file_path)
        assert len(df) == 2
        assert "title" in df.columns
        assert "venue" in df.columns
        assert df.iloc[0]["title"] == "Show 1"
        assert df.iloc[1]["title"] == "Show 2"

    @patch("src.data_storage.get_storage_config")
    def test_load_snapshot(self, mock_get_storage_config, mock_config, sample_shows):
        """Test loading a snapshot from a CSV file."""
        mock_get_storage_config.return_value = mock_config
        
        # First save a snapshot
        filename = "test_load.csv"
        save_snapshot(sample_shows, filename)
        
        # Now load it back
        loaded_shows = load_snapshot(filename)
        
        # Check that we loaded the correct number of shows
        assert len(loaded_shows) == 2
        
        # Check the content of the loaded shows
        assert loaded_shows[0].title == "Show 1"
        assert loaded_shows[1].title == "Show 2"
        assert loaded_shows[0].venue == "Theatre A"
        assert loaded_shows[1].venue == "Theatre B"

    @patch("src.data_storage.get_storage_config")
    @patch("src.data_storage.os.listdir")
    @patch("src.data_storage.os.path.getmtime")
    def test_get_latest_snapshot(self, mock_getmtime, mock_listdir, mock_get_storage_config, mock_config, sample_shows):
        """Test getting the latest snapshot filename."""
        mock_get_storage_config.return_value = mock_config
        
        # Mock the directory listing
        mock_listdir.return_value = ["theater_snapshot_20250301.csv", "theater_snapshot_20250302.csv", "theater_snapshot_20250303.csv"]
        
        # Mock the file modification times
        def mtime_side_effect(path):
            if "20250301" in path:
                return 1000  # Oldest
            if "20250302" in path:
                return 3000  # Most recent
            if "20250303" in path:
                return 2000  # Middle
            return 0
        
        mock_getmtime.side_effect = mtime_side_effect
        
        # Get the latest snapshot
        latest = get_latest_snapshot()
        
        # Check that it's the expected file
        assert latest == "theater_snapshot_20250302.csv"

    def test_compare_snapshots(self, sample_shows, modified_shows):
        """Test comparing two snapshots to detect changes."""
        # Compare the sample shows with modified shows
        comparison = compare_snapshots(modified_shows, sample_shows)
        
        # Check that the comparison results are correct
        assert len(comparison["new_shows"]) == 1
        assert comparison["new_shows"][0].title == "Show 3"
        
        assert len(comparison["updated_shows"]) == 1
        assert comparison["updated_shows"][0]["current"].title == "Show 1"
        assert comparison["updated_shows"][0]["current"].price_range == "£30-60"
        assert comparison["updated_shows"][0]["previous"].price_range == "£20-50"
        
        assert len(comparison["unchanged_shows"]) == 1
        assert comparison["unchanged_shows"][0].title == "Show 2"
        
        assert len(comparison["removed_shows"]) == 0

    @patch("src.data_storage.save_snapshot")
    @patch("src.data_storage.get_latest_snapshot")
    @patch("src.data_storage.load_snapshot")
    @patch("src.data_storage.compare_snapshots")
    def test_generate_daily_snapshot(self, mock_compare, mock_load, mock_get_latest, 
                                   mock_save, sample_shows, modified_shows):
        """Test generating a daily snapshot and comparison."""
        # Setup mocks
        mock_save.return_value = "/path/to/snapshot.csv"
        mock_get_latest.return_value = "previous_snapshot.csv"
        mock_load.return_value = sample_shows
        mock_compare.return_value = {
            "new_shows": [modified_shows[2]],
            "updated_shows": [{"current": modified_shows[0], "previous": sample_shows[0]}],
            "unchanged_shows": [modified_shows[1]],
            "removed_shows": []
        }
        
        # Call the function
        result = generate_daily_snapshot(modified_shows)
        
        # Check that the mock functions were called correctly
        mock_save.assert_called_once()
        mock_get_latest.assert_called_once()
        mock_load.assert_called_once_with("previous_snapshot.csv")
        mock_compare.assert_called_once_with(modified_shows, sample_shows)
        
        # Check the result
        assert len(result["new_shows"]) == 1
        assert len(result["updated_shows"]) == 1
        assert len(result["unchanged_shows"]) == 1
        assert len(result["removed_shows"]) == 0