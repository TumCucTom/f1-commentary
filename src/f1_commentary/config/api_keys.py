"""
API key management for external services.
"""

import os
from typing import Optional, Dict
from pathlib import Path


class APIKeyManager:
    """Manages API keys for external services."""
    
    def __init__(self, env_file: Optional[Path] = None):
        """Initialize API key manager."""
        self.env_file = env_file or Path(".env")
        self._keys: Dict[str, Optional[str]] = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Load API keys from environment variables and .env file."""
        # Load from .env file if it exists
        if self.env_file.exists():
            self._load_from_env_file()
        
        # Load from environment variables
        self._load_from_environment()
    
    def _load_from_env_file(self) -> None:
        """Load API keys from .env file."""
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key.startswith('API_KEY_') or key.endswith('_API_KEY'):
                            self._keys[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
    
    def _load_from_environment(self) -> None:
        """Load API keys from environment variables."""
        # Common API key environment variable names
        key_mappings = {
            'GROQ_API_KEY': 'groq_api_key',
            'OPENAI_API_KEY': 'openai_api_key',
            'ELEVENLABS_API_KEY': 'elevenlabs_api_key',
        }
        
        for env_var, internal_key in key_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._keys[internal_key] = value
    
    def get_key(self, service: str) -> Optional[str]:
        """Get API key for a service."""
        return self._keys.get(service)
    
    def set_key(self, service: str, key: str) -> None:
        """Set API key for a service."""
        self._keys[service] = key
    
    def has_key(self, service: str) -> bool:
        """Check if API key exists for a service."""
        return self.get_key(service) is not None
    
    def get_groq_key(self) -> Optional[str]:
        """Get Groq API key."""
        return self.get_key('groq_api_key')
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self.get_key('openai_api_key')
    
    def get_elevenlabs_key(self) -> Optional[str]:
        """Get ElevenLabs API key."""
        return self.get_key('elevenlabs_api_key')
    
    def validate_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        validation = {}
        
        # Check for required keys
        required_keys = ['groq_api_key']
        for key in required_keys:
            validation[key] = self.has_key(key)
        
        return validation
    
    def print_status(self) -> None:
        """Print API key status."""
        print("API Key Status:")
        print("=" * 40)
        
        validation = self.validate_keys()
        for key, is_valid in validation.items():
            status = "✓" if is_valid else "✗"
            print(f"{status} {key}: {'Available' if is_valid else 'Missing'}")
        
        # Show optional keys
        optional_keys = ['openai_api_key', 'elevenlabs_api_key']
        for key in optional_keys:
            is_available = self.has_key(key)
            status = "✓" if is_available else "○"
            print(f"{status} {key}: {'Available' if is_available else 'Not set'}")
