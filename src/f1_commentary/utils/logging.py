"""
Logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from ..config import get_settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> None:
    """Set up logging configuration."""
    settings = get_settings()
    
    # Use provided values or fall back to settings
    log_level = level or settings.log_level
    log_file_path = log_file or settings.log_file
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=format_string,
        handlers=_get_handlers(log_file_path)
    )
    
    # Set specific loggers
    logging.getLogger("fastf1").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def _get_handlers(log_file: Optional[Path]) -> list:
    """Get logging handlers."""
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    return handlers


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
