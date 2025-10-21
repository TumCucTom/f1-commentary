"""
Data models for commentary generation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class CommentaryType(Enum):
    """Types of commentary that can be generated."""
    INCIDENT = "incident"
    POSITION_CHANGE = "position_change"
    TRACK_LIMITS = "track_limits"
    COLLISION = "collision"
    RACE_SUMMARY = "race_summary"


@dataclass
class CommentaryResult:
    """Result of commentary generation."""
    commentary_type: CommentaryType
    commentary_text: str
    source_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.commentary_type.value,
            "commentary": self.commentary_text,
            "source_data": self.source_data,
            "metadata": self.metadata or {}
        }
