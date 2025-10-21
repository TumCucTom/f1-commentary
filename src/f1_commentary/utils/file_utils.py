"""
File and directory utilities.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Union


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp(format_string: str = "%Y%m%d_%H%M%S") -> str:
    """Get current timestamp as formatted string."""
    return datetime.now().strftime(format_string)


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing invalid characters."""
    # Remove or replace invalid characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    safe_filename = "".join(c for c in filename if c in safe_chars)
    
    # Remove multiple consecutive spaces and replace with single underscore
    safe_filename = "_".join(safe_filename.split())
    
    # Remove leading/trailing underscores and dots
    safe_filename = safe_filename.strip("_.")
    
    return safe_filename or "unnamed"


def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    return Path(path).stat().st_size


def get_directory_size(path: Union[str, Path]) -> int:
    """Get total size of directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size
