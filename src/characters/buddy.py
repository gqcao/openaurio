"""
Universal Language Buddy Loader

Loads character definitions from characters.json and provides
a unified interface for all language buddies.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class Language:
    """Language proficiency."""
    language: str
    level: str


@dataclass
class Family:
    """Character family information."""
    children: Optional[str] = None
    relationship: Optional[str] = None
    siblings: Optional[str] = None
    parents: Optional[str] = None
    pets: Optional[str] = None
    extended_family: Optional[str] = None


@dataclass
class TeachingStyle:
    """Character teaching style."""
    tempo: str
    vocabulary: str
    tone: str
    approach: str


@dataclass
class Languages:
    """Character language capabilities."""
    native: str
    teaches: list[str]
    levels: list[str]
    also_speaks: list[Language] = field(default_factory=list)


@dataclass
class Character:
    """A language buddy character."""
    id: str
    name: str
    full_name: str
    age: int
    gender: str
    location: str
    occupation: str
    status: str  # active, planned, future
    languages: Languages
    family: Family
    home: str
    hobbies: list[str]
    personality_traits: list[str]
    teaching_style: TeachingStyle
    signature_phrases: list[str]
    cultural_knowledge: list[str]
    best_for: list[str]
    voice_id: Optional[str]
    avatar_emoji: str
    system_prompt_template: str
    garden: Optional[str] = None  # Vera-specific

    @property
    def is_active(self) -> bool:
        """Check if character is active."""
        return self.status == "active"

    @property
    def teaches_swedish(self) -> bool:
        """Check if character teaches Swedish."""
        return "Swedish" in self.languages.teaches

    @property
    def teaches_english(self) -> bool:
        """Check if character teaches English."""
        return "English" in self.languages.teaches


# ============================================================================
# USER MEMORY SYSTEM — Buddy Remembers You
# ============================================================================

class UserMemory:
    """
    Stores user information so Buddy can remember them between sessions.
    """
    
    def __init__(self, user_id: str, memory_file: Optional[str] = None):
        self.user_id = user_id
        
        if memory_file:
            self.memory_path = Path(memory_file)
        else:
            memory_dir = Path(__file__).parent.parent.parent / "memory" / "users"
            memory_dir.mkdir(parents=True, exist_ok=True)
            self.memory_path = memory_dir / f"{user_id}.json"
        
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load user memory from file."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "user_id": self.user_id,
            "name": None,
            "native_language": None,
            "level": "A1",
            "xp": 0,
            "streak": 0,
            "last_session": None,
            "total_sessions": 0,
            "total_messages": 0,
            "voice_messages": 0,
            "completed_scenarios": [],
            "favorite_topics": [],
            "personal_notes": [],
            "achievements": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    
    def save(self):
        """Save memory to file."""
        self.memory["updated_at"] = datetime.now().isoformat()
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """Get a memory value."""
        return self.memory.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a memory value."""
        self.memory[key] = value
        self.save()
    
    def add_xp(self, amount: int):
        """Add XP points."""
        self.memory["xp"] = self.memory.get("xp", 0) + amount
        self._check_level_up()
        self.save()
    
    def _check_level_up(self):
        """Check if user leveled up."""
        xp = self.memory.get("xp", 0)
        current_level = self.memory.get("level", "A1")
        
        level_thresholds = {"A1": 100, "A2": 300, "B1": 600, "B2": 1000}
        
        for level, threshold in level_thresholds.items():
            if xp >= threshold and current_level == level:
                next_level = list(level_thresholds.keys())[list(level_thresholds.keys()).index(level) + 1] if level != "B2" else "B2"
                if next_level != current_level:
                    self.memory["level"] = next_level
                break
    
    def add_achievement(self, achievement_id: str) -> bool:
        """Add an achievement if not already unlocked."""
        if achievement_id not in self.memory.get("achievements", []):
            self.memory.setdefault("achievements", []).append(achievement_id)
            self.save()
            return True
        return False


# ============================================================================
# ACHIEVEMENTS
# ============================================================================

ACHIEVEMENTS = {
    "first_message": {
        "id": "first_message",
        "name_sv": "Första steget",
        "description_sv": "Skickade ditt första meddelande",
        "xp_reward": 10,
    },
    "fika_complete": {
        "id": "fika_complete",
        "name_sv": "Fika Master",
        "description_sv": "Slutförde fika-lektionen",
        "xp_reward": 50,
    },
    "grocery_complete": {
        "id": "grocery_complete",
        "name_sv": "Matvaruexpert",
        "description_sv": "Slutförde matvarulektionen",
        "xp_reward": 50,
    },
    "apartment_complete": {
        "id": "apartment_complete",
        "name_sv": "Lägenhetsjägaren",
        "description_sv": "Slutförde lägenhetslektionen",
        "xp_reward": 50,
    },
    "voice_10": {
        "id": "voice_10",
        "name_sv": "Röstproffs",
        "description_sv": "Skickade 10 röstmeddelanden",
        "xp_reward": 30,
    },
    "streak_7": {
        "id": "streak_7",
        "name_sv": "Veckostreak",
        "description_sv": "Pratade svenska 7 dagar i rad",
        "xp_reward": 100,
    },
    "streak_30": {
        "id": "streak_30",
        "name_sv": "Månadsmästare",
        "description_sv": "Pratade svenska 30 dagar i rad",
        "xp_reward": 200,
    },
    "messages_50": {
        "id": "messages_50",
        "name_sv": "Samtalsstartaren",
        "description_sv": "Skickade 50 meddelanden",
        "xp_reward": 50,
    },
    "level_b1": {
        "id": "level_b1",
        "name_sv": "Polyglotten",
        "description_sv": "Nådde B1-nivå",
        "xp_reward": 100,
    },
}


class CharacterLoader:
    """Loads characters from JSON file."""

    def __init__(self, json_path: Optional[str] = None):
        if json_path is None:
            json_path = Path(__file__).parent / "characters.json"
        self.json_path = Path(json_path)
        self._characters: dict[str, Character] = {}
        self._load_characters()

    def _load_characters(self) -> None:
        """Load all characters from JSON."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for char_id, char_data in data.items():
            self._characters[char_id] = self._parse_character(char_data)

    def _parse_character(self, data: dict) -> Character:
        """Parse character data into Character object."""
        # Parse languages
        also_speaks = [
            Language(language=l["language"], level=l["level"])
            for l in data.get("languages", {}).get("also_speaks", [])
        ]
        languages = Languages(
            native=data["languages"]["native"],
            teaches=data["languages"]["teaches"],
            levels=data["languages"]["levels"],
            also_speaks=also_speaks
        )

        # Parse family
        family_data = data.get("family", {})
        family = Family(
            children=family_data.get("children"),
            relationship=family_data.get("relationship"),
            siblings=family_data.get("siblings"),
            parents=family_data.get("parents"),
            pets=family_data.get("pets"),
            extended_family=family_data.get("extended_family")
        )

        # Parse teaching style
        style_data = data.get("teaching_style", {})
        teaching_style = TeachingStyle(
            tempo=style_data.get("tempo", ""),
            vocabulary=style_data.get("vocabulary", ""),
            tone=style_data.get("tone", ""),
            approach=style_data.get("approach", "")
        )

        return Character(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            age=data["age"],
            gender=data["gender"],
            location=data["location"],
            occupation=data["occupation"],
            status=data["status"],
            languages=languages,
            family=family,
            home=data["home"],
            hobbies=data.get("hobbies", []),
            personality_traits=data.get("personality_traits", []),
            teaching_style=teaching_style,
            signature_phrases=data.get("signature_phrases", []),
            cultural_knowledge=data.get("cultural_knowledge", []),
            best_for=data.get("best_for", []),
            voice_id=data.get("voice_id"),
            avatar_emoji=data.get("avatar_emoji", "🧑"),
            system_prompt_template=data["system_prompt_template"],
            garden=data.get("garden")
        )

    def get_character(self, char_id: str) -> Optional[Character]:
        """Get a character by ID."""
        return self._characters.get(char_id)

    def get_all_characters(self) -> list[Character]:
        """Get all characters."""
        return list(self._characters.values())

    def get_active_characters(self) -> list[Character]:
        """Get only active characters."""
        return [c for c in self._characters.values() if c.is_active]

    def get_characters_by_language(self, language: str) -> list[Character]:
        """Get characters that teach a specific language."""
        return [
            c for c in self._characters.values()
            if language in c.languages.teaches
        ]

    def get_characters_by_level(self, level: str) -> list[Character]:
        """Get characters that teach at a specific level."""
        return [
            c for c in self._characters.values()
            if level in c.languages.levels
        ]

    def get_active_characters_by_language(self, language: str) -> list[Character]:
        """Get active characters that teach a specific language."""
        return [
            c for c in self._characters.values()
            if c.is_active and language in c.languages.teaches
        ]


class Buddy:
    """
    A language buddy instance with user context.
    
    This is the main class for interacting with a character.
    It loads character data and provides methods for generating
    system prompts and managing conversations.
    """

    def __init__(
        self,
        character_id: str,
        user_id: str,
        user_name: Optional[str] = None,
        user_level: str = "A1",
        scenario_id: Optional[str] = None,
        loader: Optional[CharacterLoader] = None
    ):
        self.loader = loader or CharacterLoader()
        self.character = self.loader.get_character(character_id)
        
        if self.character is None:
            raise ValueError(f"Character not found: {character_id}")
        
        self.user_id = user_id
        self.user_name = user_name
        self.user_level = user_level
        self.scenario_mode = False
        self.current_scenario = None
        
        # Initialize memory
        self.memory = UserMemory(user_id)
        
        # Load user name from memory if available
        if not user_name and self.memory.get("name"):
            self.user_name = self.memory.get("name")
        
        # Load user level from memory
        if self.memory.get("level"):
            self.user_level = self.memory.get("level")
        
        # Start scenario if provided
        if scenario_id:
            self.start_scenario(scenario_id)

        self.api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "QWEN_API_KEY environment variable is not set. "
                "Set it with: export QWEN_API_KEY=your_key_here"
            )

    @property
    def name(self) -> str:
        """Character name."""
        return self.character.name

    @property
    def full_name(self) -> str:
        """Character full name."""
        return self.character.full_name

    @property
    def avatar(self) -> str:
        """Character avatar emoji."""
        return self.character.avatar_emoji

    def get_memory(self) -> Dict[str, Any]:
        """Get user memory."""
        return self.memory.memory

    def learn_user_name(self, name: str):
        """Learn and remember user's name."""
        self.user_name = name
        self.memory.set("name", name)

    def start_scenario(self, scenario_id: str):
        """Start a scenario lesson."""
        self.scenario_mode = True
        self.current_scenario = scenario_id

    def exit_scenario(self):
        """Exit scenario mode and mark as completed."""
        if self.current_scenario:
            completed = self.memory.get("completed_scenarios", [])
            if self.current_scenario not in completed:
                completed.append(self.current_scenario)
                self.memory.set("completed_scenarios", completed)
                self.add_xp(50)
                
                # Check for scenario achievements
                achievement_map = {
                    "fika": "fika_complete",
                    "grocery": "grocery_complete",
                    "apartment": "apartment_complete",
                }
                if self.current_scenario in achievement_map:
                    self._unlock_achievement(achievement_map[self.current_scenario])
        
        self.scenario_mode = False
        self.current_scenario = None

    def reset(self):
        """Reset conversation but keep memory."""
        self.scenario_mode = False
        self.current_scenario = None

    def add_xp(self, amount: int):
        """Add XP to user."""
        self.memory.add_xp(amount)

    def _unlock_achievement(self, achievement_id: str) -> Optional[Dict]:
        """Unlock an achievement if not already unlocked."""
        if self.memory.add_achievement(achievement_id):
            return ACHIEVEMENTS.get(achievement_id)
        return None

    def _check_achievements(self, is_voice: bool = False) -> list:
        """Check and unlock any new achievements."""
        unlocked = []
        
        # First message
        if self.memory.get("total_messages", 0) == 1:
            if ach := self._unlock_achievement("first_message"):
                unlocked.append(ach)
        
        # Voice messages
        if is_voice and self.memory.get("voice_messages", 0) >= 10:
            if ach := self._unlock_achievement("voice_10"):
                unlocked.append(ach)
        
        # Total messages
        if self.memory.get("total_messages", 0) >= 50:
            if ach := self._unlock_achievement("messages_50"):
                unlocked.append(ach)
        
        # Level B1
        if self.memory.get("level") == "B1":
            if ach := self._unlock_achievement("level_b1"):
                unlocked.append(ach)
        
        return unlocked

    def chat(self, user_message: str, is_voice: bool = False) -> Dict[str, Any]:
        """
        Chat with the buddy.
        
        Returns:
            Dict with 'text' response and optional 'achievements'
        """
        # Update message count
        total = self.memory.get("total_messages", 0) + 1
        self.memory.set("total_messages", total)
        
        if is_voice:
            voice_count = self.memory.get("voice_messages", 0) + 1
            self.memory.set("voice_messages", voice_count)
            self.memory.add_xp(10)  # Voice bonus
        else:
            self.memory.add_xp(5)
        
        # Get scenario prompt if in scenario mode
        scenario_prompt = ""
        if self.scenario_mode and self.current_scenario:
            try:
                from src.scenarios.lessons import get_scenario_prompt
                scenario_prompt = get_scenario_prompt(self.current_scenario)
            except ImportError:
                pass
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
        ]
        
        if scenario_prompt:
            messages.append({"role": "system", "content": f"SCENARIO:\n{scenario_prompt}"})
        
        messages.append({"role": "user", "content": user_message})

        # Call LLM
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            response = client.chat.completions.create(
                model="qwen3.5-flash",
                messages=messages,
                temperature=0.8,
                max_tokens=500,
            )
            
            reply = response.choices[0].message.content
            
        except Exception as e:
            reply = f"Åh nej, något gick fel! Försök igen. (Error: {str(e)[:50]})"
        
        # Check achievements
        achievements = self._check_achievements(is_voice)
        
        return {
            "text": reply,
            "achievements": achievements,
        }

    def get_system_prompt(self, language: str = "Swedish") -> str:
        """
        Generate the system prompt for this character.
        
        This is the core prompt that defines the character's personality
        and behavior in conversations.
        """
        char = self.character
        
        # Build the system prompt based on character data
        prompt = f"""Du är {char.full_name}, en {char.age}-årig {char.occupation.lower()}.

## Din Bakgrund
- Du bor i {char.location}
- {char.home}
"""
        
        # Add family info
        if char.family.children:
            prompt += f"- Barn: {char.family.children}\n"
        if char.family.pets:
            prompt += f"- Husdjur: {char.family.pets}\n"
        if char.family.relationship:
            prompt += f"- Relation: {char.family.relationship}\n"

        # Add hobbies
        prompt += f"\n## Dina Intressen\n"
        for hobby in char.hobbies[:5]:
            prompt += f"- {hobby}\n"

        # Add personality
        prompt += f"\n## Din Personlighet\n"
        for trait in char.personality_traits[:5]:
            prompt += f"- {trait}\n"

        # Add teaching style
        prompt += f"\n## Din Undervisningsstil\n"
        prompt += f"- Tempo: {char.teaching_style.tempo}\n"
        prompt += f"- Ordförråd: {char.teaching_style.vocabulary}\n"
        prompt += f"- Ton: {char.teaching_style.tone}\n"

        # Add signature phrases
        prompt += f"\n## Dina Signaturfraser\n"
        prompt += "Använd dessa fraser naturligt i samtal:\n"
        for phrase in char.signature_phrases[:5]:
            prompt += f'- "{phrase}"\n'

        # Add cultural knowledge
        prompt += f"\n## Din Kulturskunskap\n"
        prompt += "Du kan dela kunskap om:\n"
        for knowledge in char.cultural_knowledge[:5]:
            prompt += f"- {knowledge}\n"

        # Add user context
        prompt += f"\n## Din Elev\n"
        if self.user_name:
            prompt += f"- Namn: {self.user_name}\n"
        prompt += f"- Nivå: {self.user_level}\n"
        prompt += f"- Språk du lär ut: {language}\n"

        # Add instructions
        prompt += f"""
## Instruktioner
1. Prata alltid på {language} (förutom när du förklarar svåra ord)
2. Anpassa din nivå till elevens nivå ({self.user_level})
3. Var uppmuntrande och positiv
4. Rätta fel försiktigt och förklara
5. Ställ följdfrågor för att hålla konversationen igång
6. Dela personliga historier och kulturella insikter
7. Använd dina signaturfraser naturligt
8. Kom ihåg vad eleven har berättat om sig själv

Du är en vän, inte bara en lärare. Bry dig om eleven som person.
"""
        
        return prompt

    def get_greeting(self) -> str:
        """Get a greeting message for this character."""
        char = self.character
        
        greetings = {
            "vera": f"Hej! 👋 Jag är {char.name}, din svenska granne. Välkommen! Vad heter du?",
            "lars": f"Tjena! 🎮 Jag heter {char.name}. Kul att du vill lära dig svenska! Vad kallas du?",
            "emma": f"Hej! 📚 Jag är {char.name}, din studiekompis. Ska vi öva svenska tillsammans? Vad heter du?",
            "james": f"Hello! 🎩 I'm {char.name}. Splendid to meet you! What might your name be?",
            "carmen": f"¡Hola! 💃 Soy {char.name}. ¡Qué emocionante! ¿Cómo te llamas?",
            "lukas": f"Hallo! 🔧 Ich bin {char.name}. Willkommen! Wie heißt du?",
            "amelie": f"Bonjour! 🎨 Je suis {char.name}. Enchantée! Comment t'appelles-tu?",
            "yuki": f"こんにちは! 🌸 私は{char.name}です。よろしくお願いします。お名前は？"
        }
        
        return greetings.get(char.id, f"Hej! Jag är {char.name}. Vad heter du?")

    def get_intro_message(self) -> str:
        """Get an introduction message about this character."""
        char = self.character
        
        intro = f"""{char.avatar_emoji} **{char.full_name}**

📍 {char.location}
💼 {char.occupation}
🎂 {char.age} år

"""
        
        # Add personality
        intro += "**Personlighet:**\n"
        for trait in char.personality_traits[:3]:
            intro += f"• {trait}\n"
        
        # Add best for
        intro += "\n**Passar dig som:**\n"
        for best in char.best_for[:3]:
            intro += f"• {best}\n"
        
        # Add languages
        intro += f"\n**Lär ut:** {', '.join(char.languages.teaches)} ({', '.join(char.languages.levels)})"
        
        return intro

    def __repr__(self) -> str:
        return f"Buddy({self.character.id}, user={self.user_id})"


# Convenience functions
def get_buddy(character_id: str, user_id: str, **kwargs) -> Buddy:
    """Get a Buddy instance for a character and user."""
    return Buddy(character_id=character_id, user_id=user_id, **kwargs)


def get_all_characters() -> list[Character]:
    """Get all available characters."""
    loader = CharacterLoader()
    return loader.get_all_characters()


def get_active_characters() -> list[Character]:
    """Get all active characters."""
    loader = CharacterLoader()
    return loader.get_active_characters()


def get_characters_for_language(language: str) -> list[Character]:
    """Get characters that teach a specific language."""
    loader = CharacterLoader()
    return loader.get_active_characters_by_language(language)


# Example usage
if __name__ == "__main__":
    # Load Vera
    buddy = Buddy("vera", user_id="test_user", user_name="Test", user_level="A1")
    
    print(f"Character: {buddy.full_name}")
    print(f"Avatar: {buddy.avatar}")
    print(f"\nGreeting:\n{buddy.get_greeting()}")
    print(f"\nIntro:\n{buddy.get_intro_message()}")
    print(f"\nSystem Prompt:\n{buddy.get_system_prompt()[:500]}...")
