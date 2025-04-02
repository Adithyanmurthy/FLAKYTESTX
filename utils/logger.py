"""
Logging utilities for FlakyTestX.

This module provides functions for setting up and retrieving logger instances,
with support for console and file output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

# Import config settings for logging
from config import LOG_LEVEL, LOG_FILE, VERBOSE_OUTPUT

# Dictionary to store logger instances
_loggers = {}


def setup_logger(
    name: str,
    log_file: Optional[Path] = LOG_FILE,
    level: str = LOG_LEVEL,
    verbose: bool = VERBOSE_OUTPUT,
) -> logging.Logger:
    """
    Set up and configure a logger instance.

    Args:
        name: The name of the logger.
        log_file: The path to the log file. If None, only console logging is enabled.
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        verbose: Whether to enable verbose console output.

    Returns:
        The configured logger instance.
    """
    # If logger already exists, return it
    if name in _loggers:
        return _loggers[name]

    # Create logger and set level
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = False

    # Clear any existing handlers
    logger.handlers = []

    # Create console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=verbose,
        show_path=verbose,
        omit_repeated_times=not verbose,
    )
    console_handler.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)

    # Create file handler if log_file is provided
    if log_file:
        try:
            # Create directory if it doesn't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Configure file handler with rotation
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(getattr(logging, level.upper()))
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create file handler: {e}")

    # Store and return the logger
    _loggers[name] = logger
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name or create a new one.

    Args:
        name: The name of the logger to retrieve.

    Returns:
        The requested logger instance.
    """
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)