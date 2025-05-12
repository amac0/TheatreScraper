"""
Tests for the Email Notification Module

This module tests the functionality for composing and sending
email notifications about theater show updates.
"""

from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from src.models import TheaterShow
from src.notifier import (
    format_show_details,
    format_update_details,
    compose_email,
    send_email,
    notify_updates
)


@pytest.fixture
def sample_show():
    """Create a sample TheaterShow object for testing."""
    return TheaterShow(
        title="Test Show",
        venue="Test Theatre",
        url="https://example.com/test-show",
        performance_start_date=datetime(2025, 3, 1),
        performance_end_date=datetime(2025, 3, 31),
        theater_id="test_theater",
        price_range="£20-50",
        description="A test show description"
    )


@pytest.fixture
def sample_update():
    """Create a sample update (changed show) for testing."""
    previous = TheaterShow(
        title="Updated Show",
        venue="Update Theatre",
        url="https://example.com/updated-show",
        performance_start_date=datetime(2025, 4, 1),
        performance_end_date=datetime(2025, 4, 30),
        theater_id="update_theater",
        price_range="£15-45",
        description="Old description"
    )
    
    current = TheaterShow(
        title="Updated Show",
        venue="Update Theatre",
        url="https://example.com/updated-show",
        performance_start_date=datetime(2025, 4, 15),  # Changed
        performance_end_date=datetime(2025, 5, 15),    # Changed
        theater_id="update_theater",
        price_range="£20-60",  # Changed
        description="New description"  # Changed
    )
    
    return {
        'previous': previous,
        'current': current
    }


@pytest.fixture
def sample_comparison_results(sample_show, sample_update):
    """Create sample comparison results for testing."""
    return {
        'new_shows': [sample_show],
        'updated_shows': [sample_update],
        'unchanged_shows': [],
        'removed_shows': []
    }


class TestNotifier:
    """Tests for the Email Notification Module."""
    
    def test_format_show_details(self, sample_show):
        """Test formatting show details into a readable string."""
        formatted = format_show_details(sample_show)
        
        # Check that all important details are included in the output
        assert "Test Show" in formatted
        assert "Test Theatre" in formatted
        assert "https://example.com/test-show" in formatted
        assert "01 Mar 2025" in formatted  # Start date
        assert "31 Mar 2025" in formatted  # End date
        assert "£20-50" in formatted
        assert "A test show description" in formatted
    
    def test_format_update_details(self, sample_update):
        """Test formatting update details into a readable string."""
        formatted = format_update_details(sample_update)
        
        # Check that all changed fields are included in the output
        assert "Updated Show" in formatted
        assert "Update Theatre" in formatted
        assert "https://example.com/updated-show" in formatted
        assert "Start Date: 01 Apr 2025 -> 15 Apr 2025" in formatted
        assert "End Date: 30 Apr 2025 -> 15 May 2025" in formatted
        assert "Price Range: £15-45 -> £20-60" in formatted
        assert "Description has changed" in formatted
    
    def test_compose_email(self, sample_comparison_results):
        """Test composing an email from comparison results."""
        errors = ["Error 1", "Error 2"]
        email_content = compose_email(sample_comparison_results, errors)
        
        # Check the email subject and body
        assert "London Theater Updates" in email_content['subject']
        assert "# London Theater Updates" in email_content['body']
        assert "## New Shows (1)" in email_content['body']
        assert "## Updated Shows (1)" in email_content['body']
        assert "## Unchanged Shows (0)" in email_content['body']
        assert "## Errors Encountered (2)" in email_content['body']
        assert "Test Show" in email_content['body']
        assert "Updated Show" in email_content['body']
        assert "Error 1" in email_content['body']
        assert "Error 2" in email_content['body']
    
    @patch("src.notifier.get_email_config")
    @patch("src.notifier.smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, mock_get_email_config):
        """Test sending an email successfully."""
        # Mock email config
        mock_get_email_config.return_value = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "use_tls": True,
            "sender_email": "sender@example.com",
            "sender_password": "password",
            "recipient_email": "recipient@example.com"
        }
        
        # Mock SMTP connection
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Test sending email
        result = send_email({
            'subject': 'Test Subject',
            'body': 'Test Body'
        })
        
        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("sender@example.com", "password")
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
        
        # Check result
        assert result is True
    
    @patch("src.notifier.get_email_config")
    @patch("src.notifier.smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp, mock_get_email_config):
        """Test handling errors when sending email."""
        # Mock email config
        mock_get_email_config.return_value = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "use_tls": True,
            "sender_email": "sender@example.com",
            "sender_password": "password",
            "recipient_email": "recipient@example.com"
        }
        
        # Mock SMTP connection to raise an exception
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        # Test sending email
        result = send_email({
            'subject': 'Test Subject',
            'body': 'Test Body'
        })
        
        # Check result
        assert result is False
    
    @patch("src.notifier.compose_email")
    @patch("src.notifier.send_email")
    def test_notify_updates(self, mock_send_email, mock_compose_email, sample_comparison_results):
        """Test the full notification process."""
        # Mock compose_email and send_email
        mock_compose_email.return_value = {
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        mock_send_email.return_value = True
        
        # Call notify_updates
        result = notify_updates(sample_comparison_results, ["Test Error"])
        
        # Verify the mocks were called correctly
        mock_compose_email.assert_called_once_with(sample_comparison_results, ["Test Error"])
        mock_send_email.assert_called_once_with({'subject': 'Test Subject', 'body': 'Test Body'})
        
        # Check result
        assert result is True