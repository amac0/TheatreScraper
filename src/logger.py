"""
Logging module for the London Theater Show Scraper.

This module configures logging to:
- Write to daily rotating log files
- Include timestamps and log levels
- Provide different loggers for different components
"""

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Union

# Import configuration
from src.config import get_file_config

# Dictionary to track loggers that have already been set up
_loggers = {}

def setup_logger(
    name: str,
    log_level: int = logging.INFO,
    log_to_console: bool = True,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name: The name of the logger
        log_level: The logging level to use
        log_to_console: Whether to also log to the console
        log_file: Custom log file path (if None, uses the default path)
    
    Returns:
        A configured logger instance
    """
    # Get file configuration
    file_config = get_file_config()
    log_dir = file_config["log_dir"]
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplication
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Prevent propagation to parent loggers to avoid duplicate log entries
    logger.propagate = False
    
    # Create formatter with timestamps
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Determine log file path if not provided
    if log_file is None:
        log_filename = datetime.now().strftime(file_config["log_filename_format"])
        log_file = Path(log_dir) / log_filename
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Add file handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        backupCount=30,  # Keep logs for 30 days
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Optionally add console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def setup_logging(level: Union[str, int] = "INFO") -> None:
    """
    Set up the root logger and configure it for the application.
    
    This function should be called once at the beginning of the application.
    It configures the root logger, which affects all other loggers in the application.
    
    Args:
        level: Logging level (can be string like "INFO" or integer like logging.INFO)
    """
    # Reset existing loggers to avoid duplicate entries
    global _loggers
    _loggers = {}
    
    # Convert string level to integer if necessary
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Get file configuration
    file_config = get_file_config()
    log_dir = file_config["log_dir"]
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter with timestamps
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Determine log file path
    log_filename = datetime.now().strftime(file_config["log_filename_format"])
    log_file = Path(log_dir) / log_filename
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Add file handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        backupCount=30,  # Keep logs for 30 days
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create app logger - but don't add handlers as the root logger will handle it
    app_logger = logging.getLogger("theater_scraper")
    app_logger.setLevel(level)
    app_logger.handlers.clear()  # Remove any existing handlers
    
    # Make sure we're not creating duplicate log entries
    logging.getLogger("theater_scraper").propagate = True


# Create default application logger
app_logger = logging.getLogger("theater_scraper")

def get_logger(component: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger for a specific component or the main application.
    
    Args:
        component: Optional component name (e.g., 'scraper', 'storage')
    
    Returns:
        A configured logger for the specified component
    """
    if component is None:
        return app_logger
    
    logger_name = f"theater_scraper.{component}"
    
    # Check if logger already exists in our dictionary
    if logger_name in _loggers:
        return _loggers[logger_name]
    
    # Get the logger but don't add handlers if it would inherit from a parent
    logger = logging.getLogger(logger_name)
    
    # If the parent logger already has handlers, make sure we don't duplicate
    if any(isinstance(h, logging.Handler) for h in logger.parent.handlers):
        logger.propagate = True
        logger.handlers.clear()
    else:
        # Only set up handlers if parent doesn't have them
        logger = setup_logger(logger_name)
    
    _loggers[logger_name] = logger
    return logger
