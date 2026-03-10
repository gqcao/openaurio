"""
openaurio scenarios module

Conversation scenarios for practical language learning.
"""

from .lessons import (
    ScenarioLesson,
    FIKA_LESSON,
    GROCERY_LESSON,
    APARTMENT_LESSON,
    ALL_SCENARIOS,
    get_scenario,
    list_scenarios,
    get_scenario_prompt,
)

__all__ = [
    "ScenarioLesson",
    "FIKA_LESSON",
    "GROCERY_LESSON",
    "APARTMENT_LESSON",
    "ALL_SCENARIOS",
    "get_scenario",
    "list_scenarios",
    "get_scenario_prompt",
]
