# /// script
# dependencies = [
#   "openai",
#   "requests",
# ]
# ///

"""
Scenario Lessons for openaurio

Practical conversation scenarios for SFI beginners:
- Fika (coffee shop)
- Grocery shopping
- Apartment hunting
"""

import os
import json
from typing import Optional, List, Dict
from dataclasses import dataclass, field


@dataclass
class ScenarioLesson:
    """A structured conversation scenario for language practice."""
    
    id: str
    title: str
    title_sv: str  # Swedish title
    description: str
    description_sv: str
    level: str  # A1, A2, B1
    cultural_tips: List[str]
    key_phrases: List[Dict[str, str]]  # {svenska: ..., english: ...}
    scenario_prompt: str  # System prompt for this scenario
    success_criteria: List[str]  # What learner should accomplish


# ============================================================================
# SCENARIO 1: Fika ☕
# ============================================================================

FIKA_LESSON = ScenarioLesson(
    id="fika_001",
    title="Ordering Fika",
    title_sv="Beställa fika",
    description="Learn to order coffee and pastries at a Swedish café",
    description_sv="Lär dig beställa kaffe och bakverk på ett svenskt kafé",
    level="A1",
    cultural_tips=[
        "Fika is a Swedish tradition of coffee break with friends/colleagues",
        "It's common to order 'en kopp kaffe och en bulle' (coffee + cinnamon bun)",
        "You usually order at the counter, not at the table",
        "Say 'tack' when receiving your order",
    ],
    key_phrases=[
        {"svenska": "Hej, jag skulle vilja beställa en kopp kaffe", "english": "Hi, I would like to order a cup of coffee"},
        {"svenska": "Har ni några bakverk?", "english": "Do you have any pastries?"},
        {"svenska": "En kanelbulle, tack", "english": "A cinnamon bun, please"},
        {"svenska": "Vad kostar det?", "english": "How much does it cost?"},
        {"svenska": "Kan jag betala med kort?", "english": "Can I pay with card?"},
        {"svenska": "Tack så mycket!", "english": "Thank you very much!"},
    ],
    scenario_prompt="""Du är en barista på ett svenskt kafé. Du är vänlig och tålmodig med kunder som lär sig svenska.

Din roll:
- Hälsa kunden välkommen
- Ta emot beställningar på kaffe och bakverk
- Svara på frågor om priser och alternativ
- Var uppmuntrande om kunden gör misstag
- Använd enkelt språk för nybörjare

Börja med: "Hej! Välkommen till kaféet. Vad kan jag hjälpa dig med?"

Håll dina svar korta (1-2 meningar).""",
    success_criteria=[
        "Order a coffee",
        "Order a pastry",
        "Ask about the price",
        "Pay and say thank you",
    ],
)


# ============================================================================
# SCENARIO 2: Grocery Shopping 🛒
# ============================================================================

GROCERY_LESSON = ScenarioLesson(
    id="grocery_001",
    title="Grocery Shopping",
    title_sv="Handla mat",
    description="Learn to shop for groceries at a Swedish supermarket (ICA, Willys, Coop)",
    description_sv="Lär dig handla mat på en svensk stormarknad",
    level="A1",
    cultural_tips=[
        "Most stores have self-checkout (självbetjäning)",
        "You need to bag your own groceries",
        "Bring your own bags or buy them at the store",
        "Pant (bottle deposit) system exists for cans and bottles",
    ],
    key_phrases=[
        {"svenska": "Var finns mjölken?", "english": "Where is the milk?"},
        {"svenska": "Jag letar efter bröd", "english": "I'm looking for bread"},
        {"svenska": "Hur mycket kostar det?", "english": "How much does it cost?"},
        {"svenska": "Har ni ekologiska alternativ?", "english": "Do you have organic options?"},
        {"svenska": "Jag behöver en kasse", "english": "I need a bag"},
        {"svenska": "Var är självkassan?", "english": "Where is the self-checkout?"},
    ],
    scenario_prompt="""Du är en kundtjänstmedarbetare på en svensk matbutik (ICA/Willys). Du hjälper kunder att hitta varor.

Din roll:
- Hälsa kunden välkommen
- Hjälpa kunden hitta varor i butiken
- Svara på frågor om priser och produkter
- Förklara var självkassan finns
- Var tålmodig och använd enkelt språk

Börja med: "Hej! Välkommen till ICA. Kan jag hjälpa dig hitta något?"

Håll dina svar korta (1-2 meningar).""",
    success_criteria=[
        "Ask where to find an item",
        "Ask about price",
        "Ask about organic options",
        "Find the self-checkout",
    ],
)


# ============================================================================
# SCENARIO 3: Apartment Hunting 🏠
# ============================================================================

APARTMENT_LESSON = ScenarioLesson(
    id="apartment_001",
    title="Apartment Inquiry",
    title_sv="Fråga om lägenhet",
    description="Learn to inquire about renting an apartment in Sweden",
    description_sv="Lär dig fråga om att hyra en lägenhet i Sverige",
    level="A2",
    cultural_tips=[
        "Rental market is competitive, especially in big cities",
        "You often need to register with housing companies (Bostadsförmedlingen)",
        "First month's rent + deposit is usually required upfront",
        "Second-hand contracts (andrahand) are common for temporary housing",
    ],
    key_phrases=[
        {"svenska": "Hej, jag undrar om lägenheten är ledig", "english": "Hi, I wonder if the apartment is available"},
        {"svenska": "Vad är hyran per månad?", "english": "What is the rent per month?"},
        {"svenska": "Ingår el och vatten?", "english": "Are electricity and water included?"},
        {"svenska": "När kan jag flytta in?", "english": "When can I move in?"},
        {"svenska": "Kan jag få visa lägenheten?", "english": "Can I view the apartment?"},
        {"svenska": "Vad krävs för att hyra?", "english": "What is required to rent?"},
    ],
    scenario_prompt="""Du är en uthyrare som visar en lägenhet till en potentiell hyresgäst. Du är professionell och hjälpsam.

Din roll:
- Välkomna den potentiella hyresgästen
- Svara på frågor om lägenheten (hyra, storlek, faciliteter)
- Förklara vad som ingår i hyran
- Berätta om krav för att hyra
- Erbjud visning av lägenheten

Börja med: "Hej! Välkommen till visningen. Lägenheten är på 45 kvadratmeter med ett rum och kök. Vad vill du veta?"

Håll dina svar informativa men inte för långa.""",
    success_criteria=[
        "Ask if the apartment is available",
        "Ask about monthly rent",
        "Ask what's included in the rent",
        "Request a viewing",
    ],
)


# ============================================================================
# SCENARIO MANAGER
# ============================================================================

ALL_SCENARIOS: Dict[str, ScenarioLesson] = {
    "fika": FIKA_LESSON,
    "grocery": GROCERY_LESSON,
    "apartment": APARTMENT_LESSON,
}


def get_scenario(scenario_id: str) -> Optional[ScenarioLesson]:
    """Get a scenario by ID."""
    return ALL_SCENARIOS.get(scenario_id)


def list_scenarios() -> List[Dict]:
    """List all available scenarios with basic info."""
    return [
        {
            "id": s.id,
            "title": s.title,
            "title_sv": s.title_sv,
            "level": s.level,
            "description": s.description,
        }
        for s in ALL_SCENARIOS.values()
    ]


def get_scenario_prompt(scenario_id: str) -> Optional[str]:
    """Get the system prompt for a specific scenario."""
    scenario = get_scenario(scenario_id)
    return scenario.scenario_prompt if scenario else None


def main():
    """CLI to list and preview scenarios."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View openaurio scenario lessons")
    parser.add_argument("--list", action="store_true", help="List all scenarios")
    parser.add_argument("--scenario", choices=list(ALL_SCENARIOS.keys()), help="View specific scenario details")
    args = parser.parse_args()
    
    if args.list:
        print("\n📚 Available Scenario Lessons\n")
        print("=" * 50)
        for scenario in ALL_SCENARIOS.values():
            print(f"\n☕ {scenario.title_sv} ({scenario.title})")
            print(f"   Level: {scenario.level}")
            print(f"   {scenario.description}")
        print("\n" + "=" * 50)
        print(f"\nUse --scenario <id> to see details (fika, grocery, apartment)")
    
    elif args.scenario:
        scenario = ALL_SCENARIOS[args.scenario]
        print(f"\n📖 {scenario.title_sv}\n")
        print(f"Level: {scenario.level}")
        print(f"\n📝 Description:")
        print(f"   {scenario.description_sv}")
        print(f"   ({scenario.description})")
        
        print(f"\n💡 Cultural Tips:")
        for tip in scenario.cultural_tips:
            print(f"   • {tip}")
        
        print(f"\n🗣️ Key Phrases:")
        for phrase in scenario.key_phrases:
            print(f"   🇸🇪 {phrase['svenska']}")
            print(f"      🇬🇧 {phrase['english']}")
        
        print(f"\n✅ Success Criteria:")
        for criterion in scenario.success_criteria:
            print(f"   ✓ {criterion}")
        
        print(f"\n🎭 Scenario Prompt (for AI):")
        print(f"   {scenario.scenario_prompt[:200]}...")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
