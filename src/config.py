"""
Configuration module for the London Theater Show Scraper.

This module provides configuration settings for:
- Theater websites to monitor
- Email notification settings
- File paths for data storage and logs
"""

import os
from pathlib import Path
from typing import Dict, List, Union

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
LOG_DIR = DATA_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SNAPSHOT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Theater websites to monitor with their respective URLs
THEATER_URLS = {
    "donmar": "https://www.donmarwarehouse.com/whats-on",
    "bridge": "https://bridgetheatre.co.uk/performances/",
    "national": "https://www.nationaltheatre.org.uk/whats-on/",
    "hampstead": "https://www.hampsteadtheatre.com/whats-on/main-stage/",
    "marylebone": "https://www.marylebonetheatre.com/#Whats-On",
    "soho_dean": "https://sohotheatre.com/dean-street/",
    "soho_walthamstow": "https://sohotheatre.com/walthamstow/",
    "rsc": "https://www.rsc.org.uk/whats-on/in/london/?from=ql",
    "royal_court": "https://royalcourttheatre.com/whats-on/",
    "drury_lane": "https://lwtheatres.co.uk/theatres/theatre-royal-drury-lane/whats-on/"
}

# Websites that require JavaScript rendering (Selenium)
DYNAMIC_WEBSITES = ["rsc"]

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": os.environ.get("SMTP_SERVER", os.environ.get("THEATER_SMTP_SERVER", "smtp.gmail.com")),
    "smtp_port": int(os.environ.get("SMTP_PORT", os.environ.get("THEATER_SMTP_PORT", "587"))),
    "use_tls": os.environ.get("USE_TLS", os.environ.get("THEATER_SMTP_TLS", "True")).lower() == "true",
    "sender_email": os.environ.get("SENDER_EMAIL", os.environ.get("THEATER_SENDER_EMAIL", "sender@example.com")),
    "sender_password": os.environ.get("SENDER_PASSWORD", os.environ.get("THEATER_SENDER_PASSWORD", "")),
    "recipient_email": os.environ.get("RECIPIENT_EMAIL", os.environ.get("THEATER_RECIPIENT_EMAIL", "recipient@example.com")),
    "subject_prefix": "[Theater Updates] "
}

# File paths and naming conventions
FILE_CONFIG = {
    "snapshot_dir": str(SNAPSHOT_DIR),
    "log_dir": str(LOG_DIR),
    "snapshot_filename_format": "theater_data_%Y%m%d.csv",
    "log_filename_format": "theater_scraper_%Y%m%d.log"
}

# Storage configuration
STORAGE_CONFIG = {
    "snapshots_dir": str(SNAPSHOT_DIR),
}

# Scraper settings
SCRAPER_CONFIG = {
    "max_retries": 3,
    "retry_delay": 5,  # seconds
    "request_timeout": 30,  # seconds
    "user_agent": "TheaterScraperBot/1.0",
}

def get_theater_urls() -> Dict[str, str]:
    """
    Return a copy of the configured theater URLs.
    
    Returns:
        Dict[str, str]: Dictionary of theater ids and their URLs
    """
    return THEATER_URLS.copy()

def get_dynamic_websites() -> List[str]:
    """
    Return a copy of the list of websites requiring Selenium for dynamic content.
    
    Returns:
        List[str]: List of theater ids that need Selenium
    """
    return DYNAMIC_WEBSITES.copy()

def get_email_config() -> Dict[str, Union[str, int, bool]]:
    """
    Return a copy of the email configuration settings.
    
    Returns:
        Dict: Email configuration parameters
    """
    return EMAIL_CONFIG.copy()

def get_file_config() -> Dict[str, str]:
    """
    Return a copy of the file path and naming configuration.
    
    Returns:
        Dict: File configuration parameters
    """
    return FILE_CONFIG.copy()

def get_storage_config() -> Dict[str, str]:
    """
    Return a copy of the storage configuration settings.
    
    Returns:
        Dict: Storage configuration parameters
    """
    return STORAGE_CONFIG.copy()

def get_scraper_config() -> Dict[str, Union[int, str, float]]:
    """
    Return a copy of the scraper configuration settings.
    
    Returns:
        Dict: Scraper configuration parameters
    """
    return SCRAPER_CONFIG.copy()

def validate_config() -> List[str]:
    """
    Validate the configuration and return a list of issues.
    
    Returns:
        List[str]: Empty list if configuration is valid, otherwise a list of error messages
    """
    issues = []
    
    # Check essential email settings
    if any([EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["recipient_email"]]):
        for field in ["smtp_server", "sender_email", "recipient_email"]:
            if not EMAIL_CONFIG.get(field):
                issues.append(f"Missing required email config: {field}")
    
    # Check if directories are writable
    for directory in [SNAPSHOT_DIR, LOG_DIR]:
        if not os.access(directory, os.W_OK):
            issues.append(f"Directory not writable: {directory}")
    
    return issues
