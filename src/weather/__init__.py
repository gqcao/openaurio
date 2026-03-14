"""
Weather module for openaurio.

Provides weather information using wttr.in API (no API key required).
"""

from .weather import get_weather

__all__ = ["get_weather"]