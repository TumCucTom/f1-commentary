"""
Tests for utility functions.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from f1_commentary.utils import (
    setup_logging, ensure_directory, get_timestamp, 
    clean_dataframe, validate_race_data, calculate_statistics
)


def test_ensure_directory():
    """Test directory creation utility."""
    test_dir = Path("./test_dir")
    
    # Clean up if exists
    if test_dir.exists():
        test_dir.rmdir()
    
    # Test creation
    result = ensure_directory(test_dir)
    assert result.exists()
    assert result == test_dir
    
    # Clean up
    test_dir.rmdir()


def test_get_timestamp():
    """Test timestamp generation."""
    timestamp = get_timestamp()
    assert isinstance(timestamp, str)
    assert len(timestamp) == 15  # YYYYMMDD_HHMMSS format


def test_clean_dataframe():
    """Test DataFrame cleaning."""
    # Create test DataFrame with some issues
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': ['a', 'b', 'c', 'd'],
        'C': [1.1, 2.2, 3.3, 4.4]
    })
    
    # Add empty row and column
    df.loc[4] = [np.nan, np.nan, np.nan]
    df['D'] = np.nan
    
    cleaned = clean_dataframe(df)
    
    # Should remove empty row and column
    assert len(cleaned) == 4  # Original 4 rows
    assert len(cleaned.columns) == 3  # Original 3 columns


def test_validate_race_data():
    """Test race data validation."""
    # Test with minimal valid data
    valid_data = {
        'event_info': {'event_name': 'Test Race', 'date': '2024-01-01'},
        'session_results': pd.DataFrame({'Position': [1, 2, 3]}),
        'lap_data': pd.DataFrame({'LapNumber': [1, 2, 3, 4, 5]})
    }
    
    issues = validate_race_data(valid_data)
    assert len(issues['errors']) == 0
    
    # Test with missing required data
    invalid_data = {
        'event_info': {'event_name': 'Test Race'}
    }
    
    issues = validate_race_data(invalid_data)
    assert len(issues['errors']) > 0


def test_calculate_statistics():
    """Test statistics calculation."""
    df = pd.DataFrame({
        'numeric': [1, 2, 3, 4, 5],
        'text': ['a', 'b', 'a', 'c', 'b'],
        'datetime': pd.date_range('2024-01-01', periods=5)
    })
    
    # Test numeric statistics
    stats = calculate_statistics(df, 'numeric')
    assert 'mean' in stats
    assert 'std' in stats
    assert stats['mean'] == 3.0
    
    # Test text statistics
    stats = calculate_statistics(df, 'text')
    assert 'unique_values' in stats
    assert 'most_common' in stats
    assert stats['unique_values'] == 3
