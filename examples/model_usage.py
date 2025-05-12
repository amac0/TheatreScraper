"""
Example showing how to use the configuration and logging modules.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import get_theater_urls, get_email_config, validate_config
from src.logger import get_logger

def main():
    """Example usage of the configuration and logging modules."""
    # Get a logger for this component
    logger = get_logger("example")
    
    # Validate configuration
    issues = validate_config()
    if issues:
        logger.error("Configuration issues found:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return
    
    # Get theater URLs
    theaters = get_theater_urls()
    logger.info(f"Configured to monitor {len(theaters)} theaters:")
    for name, url in theaters.items():
        logger.info(f"  - {name}: {url}")
    
    # Get email config
    email_config = get_email_config()
    logger.info(f"Email notifications will be sent from {email_config['sender_email']} to {email_config['recipient_email']}")
    
    # Log a test error message
    logger.error("This is an example error message that would be logged to the file")
    
    logger.info("Example completed successfully")

if __name__ == "__main__":
    main()
