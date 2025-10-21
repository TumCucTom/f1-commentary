"""
Data processing utilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a DataFrame."""
    if df.empty:
        return df
    
    # Make a copy to avoid modifying original
    cleaned_df = df.copy()
    
    # Remove completely empty rows and columns
    cleaned_df = cleaned_df.dropna(how='all')
    cleaned_df = cleaned_df.dropna(axis=1, how='all')
    
    # Convert object columns to appropriate types where possible
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            # Try to convert to numeric
            try:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='ignore')
            except:
                pass
            
            # Try to convert to datetime
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='ignore')
                except:
                    pass
    
    return cleaned_df


def validate_race_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate race data and return any issues found."""
    issues = {
        'errors': [],
        'warnings': []
    }
    
    # Check required keys
    required_keys = ['event_info', 'session_results', 'lap_data']
    for key in required_keys:
        if key not in data:
            issues['errors'].append(f"Missing required data: {key}")
    
    # Validate event info
    if 'event_info' in data:
        event_info = data['event_info']
        if not event_info.get('event_name'):
            issues['warnings'].append("Event name is missing")
        if not event_info.get('date'):
            issues['warnings'].append("Event date is missing")
    
    # Validate session results
    if 'session_results' in data:
        results = data['session_results']
        if isinstance(results, pd.DataFrame):
            if results.empty:
                issues['errors'].append("Session results are empty")
            elif len(results) < 10:  # Expect at least 10 drivers
                issues['warnings'].append(f"Only {len(results)} drivers in results (expected ~20)")
    
    # Validate lap data
    if 'lap_data' in data:
        lap_data = data['lap_data']
        if isinstance(lap_data, pd.DataFrame):
            if lap_data.empty:
                issues['errors'].append("Lap data is empty")
            else:
                # Check for reasonable lap count
                max_lap = lap_data['LapNumber'].max() if 'LapNumber' in lap_data.columns else 0
                if max_lap < 10:
                    issues['warnings'].append(f"Very few laps recorded: {max_lap}")
                elif max_lap > 100:
                    issues['warnings'].append(f"Unusually high lap count: {max_lap}")
    
    return issues


def calculate_statistics(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate basic statistics for a DataFrame column."""
    if column not in df.columns:
        return {}
    
    series = df[column]
    
    # Handle different data types
    if pd.api.types.is_numeric_dtype(series):
        return {
            'count': len(series),
            'mean': float(series.mean()) if not series.empty else None,
            'std': float(series.std()) if not series.empty else None,
            'min': float(series.min()) if not series.empty else None,
            'max': float(series.max()) if not series.empty else None,
            'median': float(series.median()) if not series.empty else None,
            'null_count': int(series.isnull().sum())
        }
    elif pd.api.types.is_datetime64_any_dtype(series):
        return {
            'count': len(series),
            'earliest': series.min().isoformat() if not series.empty else None,
            'latest': series.max().isoformat() if not series.empty else None,
            'null_count': int(series.isnull().sum())
        }
    else:
        # Categorical/text data
        value_counts = series.value_counts()
        return {
            'count': len(series),
            'unique_values': int(series.nunique()),
            'most_common': value_counts.head(5).to_dict() if not value_counts.empty else {},
            'null_count': int(series.isnull().sum())
        }


def merge_telemetry_data(telemetry_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge multiple telemetry DataFrames into one."""
    if not telemetry_dict:
        return pd.DataFrame()
    
    merged_data = []
    for driver, data in telemetry_dict.items():
        if not data.empty:
            data_copy = data.copy()
            data_copy['Driver'] = driver
            merged_data.append(data_copy)
    
    if merged_data:
        return pd.concat(merged_data, ignore_index=True)
    else:
        return pd.DataFrame()
