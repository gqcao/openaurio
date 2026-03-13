"""
openaurio characters module

AI character personas for language learning conversations.

Usage:
    from characters import Buddy, get_buddy, get_all_characters
    
    buddy = get_buddy("vera", user_id="123", user_name="Alice")
    prompt = buddy.get_system_prompt()
"""

from .buddy import (
    Buddy,
    Character,
    CharacterLoader,
    Language,
    Family,
    TeachingStyle,
    Languages,
    get_buddy,
    get_all_characters,
    get_active_characters,
    get_characters_for_language,
)

__all__ = [
    "Buddy",
    "Character",
    "CharacterLoader",
    "Language",
    "Family",
    "TeachingStyle",
    "Languages",
    "get_buddy",
    "get_all_characters",
    "get_active_characters",
    "get_characters_for_language",
]