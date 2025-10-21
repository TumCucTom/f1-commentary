"""
Application settings and configuration management.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    groq_api_key: Optional[str] = None
    
    # Data Directories
    cache_dir: Path = field(default_factory=lambda: Path("./f1_cache"))
    output_dir: Path = field(default_factory=lambda: Path("./f1_data_output"))
    analysis_dir: Path = field(default_factory=lambda: Path("./analysis_results"))
    visualization_dir: Path = field(default_factory=lambda: Path("./incident_visualizations"))
    
    # Default Models
    default_groq_model: str = "llama-3.1-8b-instant"
    
    # Visualization Settings
    default_car_size: int = 25
    default_follow_window: float = 200.0
    default_fps: int = 30
    
    # Analysis Settings
    min_position_change: int = 3
    max_incidents_to_analyze: int = 5
    max_position_changes_to_analyze: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    def __post_init__(self):
        """Initialize settings after creation."""
        # Create directories if they don't exist
        for directory in [self.cache_dir, self.output_dir, self.analysis_dir, self.visualization_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Load API keys from environment
        self.groq_api_key = self.groq_api_key or os.getenv("GROQ_API_KEY")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "groq_api_key": self.groq_api_key,
            "cache_dir": str(self.cache_dir),
            "output_dir": str(self.output_dir),
            "analysis_dir": str(self.analysis_dir),
            "visualization_dir": str(self.visualization_dir),
            "default_groq_model": self.default_groq_model,
            "default_car_size": self.default_car_size,
            "default_follow_window": self.default_follow_window,
            "default_fps": self.default_fps,
            "min_position_change": self.min_position_change,
            "max_incidents_to_analyze": self.max_incidents_to_analyze,
            "max_position_changes_to_analyze": self.max_position_changes_to_analyze,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_settings(**kwargs) -> None:
    """Update global settings with new values."""
    global _settings
    if _settings is None:
        _settings = Settings()
    
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
        else:
            raise ValueError(f"Unknown setting: {key}")
