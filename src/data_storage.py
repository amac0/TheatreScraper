"""
Data Storage Module

This module handles saving and loading theater show data as CSV snapshots,
as well as comparing snapshots to detect changes over time.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from src.config import get_storage_config
from src.logger import get_logger
from src.models import TheaterShow

# Initialize logger
logger = get_logger("data_storage")


def save_snapshot(shows: List[TheaterShow], filename: Optional[str] = None) -> str:
    """
    Save a list of TheaterShow objects to a CSV file.
    
    Args:
        shows: List of TheaterShow objects to save
        filename: Optional filename for the CSV; if not provided, a default name with 
                 current date will be used
                 
    Returns:
        The path to the saved CSV file
    """
    config = get_storage_config()
    snapshots_dir = Path(config["snapshots_dir"])
    
    # Create snapshots directory if it doesn't exist
    os.makedirs(snapshots_dir, exist_ok=True)
    
    # Generate filename with current date if not provided
    if not filename:
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"theater_snapshot_{date_str}.csv"
    
    # Convert shows to a list of dictionaries for pandas
    shows_data = [show.to_dict() for show in shows]
    
    # Convert to DataFrame
    df = pd.DataFrame(shows_data)
    
    # Save to CSV
    file_path = snapshots_dir / filename
    df.to_csv(file_path, index=False)
    logger.info(f"Saved {len(shows)} shows to {file_path}")
    
    return str(file_path)


def load_snapshot(filename: str) -> List[TheaterShow]:
    """
    Load shows from a CSV snapshot file.
    
    Args:
        filename: Name of the CSV file to load
        
    Returns:
        List of TheaterShow objects
    """
    config = get_storage_config()
    snapshots_dir = Path(config["snapshots_dir"])
    file_path = snapshots_dir / filename
    
    if not os.path.exists(file_path):
        logger.error(f"Snapshot file not found: {file_path}")
        return []
    
    try:
        # Load CSV into DataFrame
        df = pd.read_csv(file_path)
        
        # Convert rows to TheaterShow objects
        shows = []
        for _, row in df.iterrows():
            show_dict = row.to_dict()
            shows.append(TheaterShow.from_dict(show_dict))
        
        logger.info(f"Loaded {len(shows)} shows from {file_path}")
        return shows
    
    except Exception as e:
        logger.error(f"Error loading snapshot {file_path}: {str(e)}")
        return []


def get_latest_snapshot() -> Optional[str]:
    """
    Get the filename of the most recent snapshot in the snapshots directory.
    
    Returns:
        The filename of the most recent snapshot, or None if no snapshots exist
    """
    config = get_storage_config()
    snapshots_dir = Path(config["snapshots_dir"])
    
    if not os.path.exists(snapshots_dir):
        logger.warning(f"Snapshots directory does not exist: {snapshots_dir}")
        return None
    
    # Get all CSV files in the snapshots directory
    csv_files = [f for f in os.listdir(snapshots_dir) if f.endswith('.csv') and f.startswith('theater_snapshot_')]
    
    if not csv_files:
        logger.warning("No snapshot files found")
        return None
    
    # Sort by modification time (most recent first)
    csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(snapshots_dir, f)), reverse=True)
    
    return csv_files[0]


def compare_snapshots(current_shows: List[TheaterShow], previous_shows: List[TheaterShow]) -> Dict:
    """
    Compare two snapshots to detect changes.
    
    Args:
        current_shows: List of current TheaterShow objects
        previous_shows: List of previous TheaterShow objects
        
    Returns:
        Dictionary with lists of new, updated, and unchanged shows
    """
    # Create dictionaries for easier comparison, using title and venue as the key
    current_dict = {(show.title, show.venue): show for show in current_shows}
    previous_dict = {(show.title, show.venue): show for show in previous_shows}
    
    # Identify new, updated, and unchanged shows
    new_shows = []
    updated_shows = []
    unchanged_shows = []
    
    # Check for new and updated shows
    for key, current_show in current_dict.items():
        if key not in previous_dict:
            # Show is new
            new_shows.append(current_show)
        else:
            # Show exists in both snapshots, check for updates
            previous_show = previous_dict[key]
            
            # Compare relevant fields
            if (current_show.performance_start_date != previous_show.performance_start_date or
                    current_show.performance_end_date != previous_show.performance_end_date or
                    current_show.price_range != previous_show.price_range or
                    current_show.description != previous_show.description):
                # Show has been updated
                updated_shows.append({
                    'current': current_show,
                    'previous': previous_show
                })
            else:
                # Show is unchanged
                unchanged_shows.append(current_show)
    
    # Identify removed shows (in previous but not in current)
    removed_shows = [show for key, show in previous_dict.items() if key not in current_dict]
    
    logger.info(f"Comparison results: {len(new_shows)} new, {len(updated_shows)} updated, "
                f"{len(unchanged_shows)} unchanged, {len(removed_shows)} removed")
    
    return {
        'new_shows': new_shows,
        'updated_shows': updated_shows,
        'unchanged_shows': unchanged_shows,
        'removed_shows': removed_shows
    }


def generate_daily_snapshot(current_shows: List[TheaterShow]) -> Dict:
    """
    Generate a daily snapshot and compare with the previous snapshot.
    
    Args:
        current_shows: List of current TheaterShow objects
        
    Returns:
        Dictionary with comparison results
    """
    # Save current snapshot
    today = datetime.now().strftime("%Y%m%d")
    filename = f"theater_snapshot_{today}.csv"
    save_snapshot(current_shows, filename)
    
    # Find the latest previous snapshot
    previous_filename = get_latest_snapshot()
    
    # If the latest snapshot is the one we just created, try to find an older one
    if previous_filename == filename:
        config = get_storage_config()
        snapshots_dir = Path(config["snapshots_dir"])
        csv_files = [f for f in os.listdir(snapshots_dir) if f.endswith('.csv') and f.startswith('theater_snapshot_')]
        
        if len(csv_files) > 1:
            # Sort by modification time (oldest to newest)
            csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(snapshots_dir, f)))
            # Take the second-to-last file
            previous_filename = csv_files[-2]
        else:
            # No previous snapshot to compare with
            logger.info("No previous snapshot available for comparison")
            return {
                'new_shows': current_shows,
                'updated_shows': [],
                'unchanged_shows': [],
                'removed_shows': []
            }
    
    # Load previous snapshot and compare
    previous_shows = load_snapshot(previous_filename)
    return compare_snapshots(current_shows, previous_shows)