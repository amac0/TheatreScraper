"""
Unit tests for the configuration module.
"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

# Import functions to test
from src.config import (
    get_theater_urls,
    get_dynamic_websites,
    get_email_config,
    get_file_config,
    get_scraper_config,
    validate_config,
    THEATER_URLS,
    EMAIL_CONFIG
)

def test_theater_urls_not_empty():
    """Test that theater URLs dictionary is not empty and contains expected theaters."""
    urls = get_theater_urls()
    assert urls, "Theater URLs dictionary should not be empty"
    assert len(urls) >= 10, "Should contain at least 10 theater URLs"
    assert "donmar" in urls, "Donmar Warehouse should be in URLs"
    assert "bridge" in urls, "Bridge Theatre should be in URLs"
    assert "national" in urls, "National Theatre should be in URLs"

def test_get_theater_urls_returns_copy():
    """Test that get_theater_urls returns a copy to prevent accidental modification."""
    urls = get_theater_urls()
    
    # Try to modify the returned dictionary
    urls["test_theater"] = "https://test.com"
    
    # Verify original is unchanged
    assert "test_theater" not in THEATER_URLS, "Original THEATER_URLS should not be modified"

def test_get_dynamic_websites():
    """Test that the dynamic websites list contains expected values."""
    dynamic_sites = get_dynamic_websites()
    assert "rsc" in dynamic_sites, "RSC should be in dynamic websites list"

def test_get_email_config():
    """Test that email configuration contains all required fields."""
    email_config = get_email_config()
    
    # Check required fields
    required_fields = [
        "smtp_server", "smtp_port", "use_tls", 
        "sender_email", "sender_password", "recipient_email"
    ]
    
    for field in required_fields:
        assert field in email_config, f"Email config missing field: {field}"

def test_get_file_config():
    """Test that file configuration contains all required fields."""
    file_config = get_file_config()
    
    # Check required fields
    required_fields = [
        "snapshot_dir", "log_dir",
        "snapshot_filename_format", "log_filename_format"
    ]
    
    for field in required_fields:
        assert field in file_config, f"File config missing field: {field}"

def test_get_scraper_config():
    """Test that scraper configuration contains all required fields."""
    scraper_config = get_scraper_config()
    
    # Check required fields
    required_fields = [
        "max_retries", "retry_delay", "request_timeout", "user_agent"
    ]
    
    for field in required_fields:
        assert field in scraper_config, f"Scraper config missing field: {field}"

def test_validate_config_with_valid_config():
    """Test validation with a valid configuration."""
    with patch('os.access', return_value=True):  # Assume directories are writable
        issues = validate_config()
        assert not issues, f"Expected no validation issues but found: {issues}"

def test_validate_config_with_invalid_email():
    """Test validation with invalid email configuration."""
    # Create a backup of original values
    original_sender = EMAIL_CONFIG["sender_email"]
    original_recipient = EMAIL_CONFIG["recipient_email"]
    
    try:
        # Set invalid values
        EMAIL_CONFIG["sender_email"] = ""
        EMAIL_CONFIG["recipient_email"] = "recipient@example.com"
        
        with patch('os.access', return_value=True):  # Assume directories are writable
            issues = validate_config()
            assert any("Missing required email config: sender_email" in issue for issue in issues)
    finally:
        # Restore original values
        EMAIL_CONFIG["sender_email"] = original_sender
        EMAIL_CONFIG["recipient_email"] = original_recipient

def test_validate_config_with_nonwritable_directory():
    """Test validation with non-writable directories."""
    with patch('os.access', return_value=False):  # Simulate non-writable directories
        issues = validate_config()
        assert any("Directory not writable" in issue for issue in issues)
