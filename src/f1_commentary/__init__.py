"""
F1 Commentary Package

A comprehensive toolkit for F1 race data collection, analysis, commentary generation,
and visualization.

Modules:
- data: F1 race data collection and processing
- analysis: Race analysis and incident detection
- commentary: AI-powered commentary generation
- visualization: Race incident visualization and animation
- utils: Common utilities and helpers
- config: Configuration management
"""

__version__ = "1.0.0"
__author__ = "F1 Commentary Team"

from .data import F1DataCollector
from .analysis import F1RaceAnalyzer
from .commentary import F1CommentaryGenerator
from .visualization import F1IncidentVisualizer

__all__ = [
    "F1DataCollector",
    "F1RaceAnalyzer", 
    "F1CommentaryGenerator",
    "F1IncidentVisualizer"
]
