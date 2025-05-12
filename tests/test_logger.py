"""
Unit tests for the logging module.
"""

import logging
import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from src.logger import setup_logger, get_logger

def test_setup_logger_creates_proper_logger():
    """Test that setup_logger creates a properly configured logger."""
    # Create a temporary log file for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_file = Path(temp_dir) / "test.log"
        
        # Create the logger
        logger = setup_logger(
            "test_logger",
            log_level=logging.DEBUG,
            log_to_console=False,
            log_file=temp_log_file
        )
        
        # Verify logger configuration
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1  # Should have one file handler
        
        # Test log message
        test_message = "Test log message"
        logger.debug(test_message)
        
        # Verify the log was written to the file
        assert temp_log_file.exists(), "Log file should be created"
        
        with open(temp_log_file, "r") as f:
            log_content = f.read()
            assert test_message in log_content, "Log file should contain the test message"

def test_setup_logger_with_console_output():
    """Test that setup_logger properly configures console output when requested."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log_file = Path(temp_dir) / "test.log"
        
        logger = setup_logger(
            "test_console_logger",
            log_level=logging.INFO,
            log_to_console=True,
            log_file=temp_log_file
        )
        
        # Should have both file and console handlers
        assert len(logger.handlers) == 2
        
        # Verify handler types
        handler_types = [type(handler) for handler in logger.handlers]
        assert logging.StreamHandler in handler_types, "Should have StreamHandler for console output"

def test_get_logger_default():
    """Test that get_logger returns the default application logger when no component is specified."""
    logger = get_logger()
    assert logger.name == "theater_scraper", "Default logger should be named 'theater_scraper'"

def test_get_logger_component():
    """Test that get_logger returns a properly named component logger."""
    component_name = "scraper"
    logger = get_logger(component_name)
    
    expected_name = f"theater_scraper.{component_name}"
    assert logger.name == expected_name, f"Component logger should be named '{expected_name}'"

@patch('src.logger.setup_logger')
def test_get_logger_calls_setup_logger(mock_setup_logger):
    """Test that get_logger calls setup_logger with the correct parameters."""
    # Configure the mock
    mock_logger = MagicMock()
    mock_setup_logger.return_value = mock_logger
    
    # Call get_logger
    component_name = "test_component"
    result = get_logger(component_name)
    
    # Verify setup_logger was called
    expected_name = f"theater_scraper.{component_name}"
    mock_setup_logger.assert_called_once_with(expected_name)
    
    # Verify the result
    assert result == mock_logger
