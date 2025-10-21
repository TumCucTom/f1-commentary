"""
Tests for configuration management.
"""

import pytest
from pathlib import Path
from f1_commentary.config import Settings, get_settings, APIKeyManager


def test_settings_creation():
    """Test settings creation and defaults."""
    settings = Settings()
    
    assert settings.cache_dir.exists()
    assert settings.output_dir.exists()
    assert settings.analysis_dir.exists()
    assert settings.visualization_dir.exists()
    assert settings.default_groq_model == "llama-3.1-8b-instant"


def test_settings_to_dict():
    """Test settings to dictionary conversion."""
    settings = Settings()
    settings_dict = settings.to_dict()
    
    assert isinstance(settings_dict, dict)
    assert "cache_dir" in settings_dict
    assert "output_dir" in settings_dict
    assert "default_groq_model" in settings_dict


def test_get_settings_singleton():
    """Test that get_settings returns a singleton."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_api_key_manager():
    """Test API key manager functionality."""
    key_manager = APIKeyManager()
    
    # Test setting and getting keys
    key_manager.set_key("test_key", "test_value")
    assert key_manager.get_key("test_key") == "test_value"
    assert key_manager.has_key("test_key") is True
    
    # Test validation
    validation = key_manager.validate_keys()
    assert isinstance(validation, dict)
