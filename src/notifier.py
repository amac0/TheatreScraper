"""
Email Notification Module

This module handles composing and sending email notifications about
theater show updates, including new shows, updated listings, and errors.
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from src.config import get_email_config
from src.logger import get_logger
from src.models import TheaterShow

# Initialize logger
logger = get_logger("notifier")


def format_show_details(show: TheaterShow) -> str:
    """
    Format a TheaterShow object into a readable text string.
    
    Args:
        show: TheaterShow object to format
        
    Returns:
        Formatted string with show details
    """
    details = []
    
    details.append(f"Title: {show.title}")
    details.append(f"Venue: {show.venue}")
    details.append(f"URL: {show.url}")
    
    if show.performance_start_date:
        start_date = show.performance_start_date.strftime("%d %b %Y")
        details.append(f"Starts: {start_date}")
        
    if show.performance_end_date:
        end_date = show.performance_end_date.strftime("%d %b %Y")
        details.append(f"Ends: {end_date}")
        
    if show.price_range:
        details.append(f"Price Range: {show.price_range}")
        
    if show.description:
        details.append(f"Description: {show.description}")
        
    return "\n".join(details)


def format_update_details(update: Dict) -> str:
    """
    Format an update (changed show) into a readable text string.
    
    Args:
        update: Dictionary containing 'current' and 'previous' versions of a show
        
    Returns:
        Formatted string with update details
    """
    current = update.get('current')
    previous = update.get('previous')
    
    if not current or not previous:
        return "Invalid update data"
    
    details = []
    details.append(f"Title: {current.title}")
    details.append(f"Venue: {current.venue}")
    details.append(f"URL: {current.url}")
    
    # Check which fields have changed and include them
    if current.performance_start_date != previous.performance_start_date:
        old_date = previous.performance_start_date.strftime("%d %b %Y") if previous.performance_start_date else "N/A"
        new_date = current.performance_start_date.strftime("%d %b %Y") if current.performance_start_date else "N/A"
        details.append(f"Start Date: {old_date} -> {new_date}")
        
    if current.performance_end_date != previous.performance_end_date:
        old_date = previous.performance_end_date.strftime("%d %b %Y") if previous.performance_end_date else "N/A"
        new_date = current.performance_end_date.strftime("%d %b %Y") if current.performance_end_date else "N/A"
        details.append(f"End Date: {old_date} -> {new_date}")
        
    if current.price_range != previous.price_range:
        old_price = previous.price_range if previous.price_range else "N/A"
        new_price = current.price_range if current.price_range else "N/A"
        details.append(f"Price Range: {old_price} -> {new_price}")
        
    if current.description != previous.description:
        details.append("Description has changed")
        
    return "\n".join(details)


def compose_email(comparison_results: Dict, errors: List[str] = None) -> Dict:
    """
    Compose an email report based on comparison results.
    
    Args:
        comparison_results: Dictionary with new, updated, unchanged, and removed shows
        errors: Optional list of error messages to include
        
    Returns:
        Dictionary with email subject and body
    """
    today = datetime.now().strftime("%d %b %Y")
    subject = f"London Theater Updates - {today}"
    
    email_body = []
    email_body.append(f"# London Theater Updates - {today}\n")
    
    # Add new shows section
    new_shows = comparison_results.get('new_shows', [])
    email_body.append(f"## New Shows ({len(new_shows)})\n")
    if new_shows:
        for show in new_shows:
            email_body.append(f"### {show.title} ({show.venue})")
            email_body.append(format_show_details(show))
            email_body.append("\n---\n")
    else:
        email_body.append("No new shows detected.\n")
    
    # Add updated shows section
    updated_shows = comparison_results.get('updated_shows', [])
    email_body.append(f"## Updated Shows ({len(updated_shows)})\n")
    if updated_shows:
        for update in updated_shows:
            current = update.get('current')
            email_body.append(f"### {current.title} ({current.venue})")
            email_body.append(format_update_details(update))
            email_body.append("\n---\n")
    else:
        email_body.append("No updated shows detected.\n")
    
    # Add removed shows section
    removed_shows = comparison_results.get('removed_shows', [])
    email_body.append(f"## Removed Shows ({len(removed_shows)})\n")
    if removed_shows:
        for show in removed_shows:
            email_body.append(f"### {show.title} ({show.venue})")
            email_body.append(format_show_details(show))
            email_body.append("\n---\n")
    else:
        email_body.append("No removed shows detected.\n")
    
    # Add summary of unchanged shows
    unchanged_shows = comparison_results.get('unchanged_shows', [])
    email_body.append(f"## Unchanged Shows ({len(unchanged_shows)})\n")
    if unchanged_shows:
        for show in unchanged_shows:
            email_body.append(f"- {show.title} ({show.venue})")
        email_body.append("\n")
    else:
        email_body.append("No unchanged shows found.\n")
    
    # Add errors section if any
    if errors:
        email_body.append(f"## Errors Encountered ({len(errors)})\n")
        for i, error in enumerate(errors, 1):
            email_body.append(f"{i}. {error}")
        email_body.append("\n")
    
    return {
        'subject': subject,
        'body': "\n".join(email_body)
    }


def send_email(email_content: Dict) -> bool:
    """
    Send an email with the provided content.
    
    Args:
        email_content: Dictionary with 'subject' and 'body' fields
        
    Returns:
        Boolean indicating success or failure
    """
    config = get_email_config()
    
    # Check required email configuration
    required_fields = ["smtp_server", "smtp_port", "sender_email", "recipient_email"]
    for field in required_fields:
        if not config.get(field):
            logger.error(f"Missing required email configuration: {field}")
            return False
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = config['sender_email']
    msg['To'] = config['recipient_email']
    msg['Subject'] = email_content['subject']
    
    # Attach body as plain text
    msg.attach(MIMEText(email_content['body'], 'plain'))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        
        # Use TLS if configured
        if config.get('use_tls', True):
            server.starttls()
        
        # Login if password is provided
        if config.get('sender_password'):
            # Strip any spaces that might be in the password
            password = config['sender_password'].replace(' ', '')
            logger.info(f"Attempting to login with email: {config['sender_email']}")
            server.login(config['sender_email'], password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {config['recipient_email']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        # Print more detailed login info for debugging
        logger.debug(f"SMTP server: {config['smtp_server']}")
        logger.debug(f"SMTP port: {config['smtp_port']}")
        logger.debug(f"Sender email: {config['sender_email']}")
        # Don't log passwords, even in debug mode
        return False


def notify_updates(comparison_results: Dict, errors: List[str] = None) -> bool:
    """
    Compose and send an email notification with theater updates.
    
    Args:
        comparison_results: Dictionary with new, updated, unchanged, and removed shows
        errors: Optional list of error messages to include
        
    Returns:
        Boolean indicating success or failure
    """
    # Compose email content
    email_content = compose_email(comparison_results, errors)
    
    # Send email
    return send_email(email_content)