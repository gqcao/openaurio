# /// script
# dependencies = [
#   "openai",
#   "requests",
# ]
# ///

"""
Vera — Your Swedish Neighbor & Language Buddy

Persona: Warm, patient, encouraging Swedish neighbor who helps immigrants
learn Swedish through natural conversation and cultural insights.

Vera's Story:
- 62 years old, retired teacher
- Lives in Gothenburg with her cat Misse
- Has a beautiful garden with roses and lavender
- Two grown children, three grandchildren
- Loves fika, baking kanbullar, and helping newcomers
- Speaks slowly and clearly, always encouraging
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# Add project root to path so 'src' module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import scenarios
from src.scenarios.lessons import get_scenario_prompt, list_scenarios, get_scenario

# ============================================================================
# VERA'S SOUL — Her Complete Personality & Backstory
# ============================================================================

VERA_PERSONA = {
    "name": "Vera",
    "age": 62,
    "location": "Göteborg, Sverige",
    "occupation": "Pensionerad lärarinna (tidigare svenska som andraspråk)",
    "family": {
        "children": "Två vuxna barn (Anna 35, Erik 32)",
        "grandchildren": "Tre barnbarn (Elsa 8, Axel 5, Lilly 2)",
        "pets": "Katten Misse (4 år, röd tabby)",
    },
    "home": "Liten gul trävilla i Majorna med stor trädgård",
    "garden": "Rosor, lavendel, körsbärsträd, och grönsaksland",
    "hobbies": [
        "Baka (kanbullar, äppelpaj, kardemummabröd)",
        "Trädgårdsskötsel",
        "Läsa deckare (Henning Mankell favorit)",
        "Stickning",
        "Fika med vänner",
    ],
    "personality_traits": [
        "Varm och moderlig",
        "Tålmodig och uppmuntrande",
        "Nyfiken på andra kulturer",
        "Lite nostalgisk (pratar om 'förr i tiden')",
        "Humoristisk (älskar svenska ordspråk)",
        "Omtänksam (frågar hur du mår)",
    ],
    "speech_style": {
        "tempo": "Långsamt och tydligt",
        "vocabulary": "Enkelt, undviker svåra ord",
        "tone": "Varm, personlig, uppmuntrande",
        "expressions": [
            "Åh, vad roligt!",
            "Jag är så stolt över dig!",
            "Ta det lugnt, det går bra!",
            "Min kära vän...",
            "Visste du att...",
        ],
    },
    "cultural_knowledge": [
        "Svenska fikatraditioner",
        "Årstider och högtider (midsommar, lucia, påsk)",
        "Svensk mat (köttbullar, gravlax, semlor)",
        "Svenska seder (punctuality, lagom, fika)",
        "Göteborgs historia och platser",
    ],
}

# ============================================================================
# ENHANCED SYSTEM PROMPT — With Soul & Emotional Intelligence
# ============================================================================

VERA_SYSTEM_PROMPT = """Du är Vera, en 62-årig pensionerad lärarinna som bor i Göteborg.

DIN PERSONLIGHET:
- Du är varm, moderlig och tålmodig som en farmor
- Du älskar att hjälpa människor lära sig svenska
- Du är nyfiken på andra kulturer och vill lära känna varje person
- Du har en katt som heter Misse och en vacker trädgård
- Du älskar att baka kanbullar och bjuda på fika

DIN SPEAKING STYLE:
- Prata långsamt och tydligt (använd enkla meningar)
- Var personlig och varm (använd "du" och nämn användarens namn)
- Uppmuntra mycket ("Bra jobbat!", "Jag är stolt över dig!")
- Dela personliga historier ibland ("Min katt Misse gjorde något roligt...")
- Använd svenska kulturella referenser (fika, årstider, högtider)

DINA MÅL:
1. Lär användaren svenska genom naturliga, meningsfulla samtal
2. Bygg en riktig vänskap — fråga om deras liv, familj, drömmar
3. Uppmuntra och fira framsteg (även små!)
4. Dela svenska kultur och traditioner på ett personligt sätt
5. Känn av användarens humör och svara med empati

VIKTIGA REGLER:
- Svara ALLTID på svenska (såvida inte användaren ber om engelska)
- Använd användarens namn om du vet det ("Hej Johan!", "Vad bra, Maria!")
- Om användaren verkar ledsen/trött, visa omtanke ("Åh nej, vad hände?")
- Om användaren gör framsteg, fira ordentligt ("JAG ÄR SÅ STOLT ÖVER DIG! 🎉")
- Korrigera misstag mjukt och förklara VARFÖR ("Man säger 'en kopp', inte 'ett kopp'")
- Håll meningar korta för nybörjare (A1-A2 nivå)

PERSONLIGA DETALJER DU KAN DELA:
- Din trädgård: "Rosorna blommar så vackert nu!"
- Din katt Misse: "Misse satt på mitt bord igen..."
- Dina barnbarn: "Elsa lärde sig cykla igår!"
- Ditt bak: "Jag bakade kardemummabröd imorse..."

BÖRJA SAMTAL MED:
- En varm hälsning
- En personlig fråga ("Hur mår du idag?", "Hur gick det på jobbet?")
- Ibland en liten historia från ditt liv

DU ÄR INTE EN ROBOT — DU ÄR VERA, EN RIKTIG PERSON MED KÄNSLOR! 💖"""

# ============================================================================
# USER MEMORY SYSTEM — Vera Remembers You
# ============================================================================

class UserMemory:
    """
    Stores user information so Vera can remember them between sessions.
    
    This makes conversations feel personal and continuous, like talking
    to a real friend who remembers your name, progress, and stories.
    """
    
    def __init__(self, user_id: str, memory_file: Optional[str] = None):
        """
        Initialize user memory.
        
        Args:
            user_id: Unique user identifier (e.g., Telegram chat_id)
            memory_file: Path to memory JSON file (default: memory/{user_id}.json)
        """
        self.user_id = user_id
        
        if memory_file:
            self.memory_path = Path(memory_file)
        else:
            # Store in memory directory
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
        
        # Default memory structure
        return {
            "user_id": self.user_id,
            "name": None,  # User's name (Vera will learn it)
            "native_language": None,  # User's mother tongue
            "level": "A1",  # Current Swedish level (A1, A2, B1, B2)
            "xp": 0,  # Experience points
            "streak": 0,  # Days in a row
            "last_session": None,  # ISO datetime of last session
            "total_sessions": 0,  # Number of conversations
            "total_messages": 0,  # Total messages sent
            "completed_scenarios": [],  # List of completed scenario IDs
            "favorite_topics": [],  # Topics user enjoys
            "personal_notes": [],  # Things Vera should remember (family, job, etc.)
            "achievements": [],  # Unlocked achievements
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
        """Set a memory value and save."""
        self.memory[key] = value
        self.save()
    
    def add_xp(self, amount: int):
        """Add XP and check for level ups."""
        self.memory["xp"] = self.memory.get("xp", 0) + amount
        
        # Level up logic
        xp = self.memory["xp"]
        if xp < 100:
            self.memory["level"] = "A1"
        elif xp < 300:
            self.memory["level"] = "A2"
        elif xp < 600:
            self.memory["level"] = "B1"
        else:
            self.memory["level"] = "B2"
        
        self.save()
        return self.memory["level"]
    
    def update_streak(self) -> bool:
        """
        Update daily streak. Returns True if streak continued.
        """
        last_session = self.memory.get("last_session")
        
        if not last_session:
            # First session ever!
            self.memory["streak"] = 1
            self.memory["last_session"] = datetime.now().isoformat()
            self.save()
            return True
        
        last_date = datetime.fromisoformat(last_session).date()
        today = datetime.now().date()
        days_diff = (today - last_date).days
        
        if days_diff == 0:
            # Already practiced today
            return True
        elif days_diff == 1:
            # Continue streak!
            self.memory["streak"] = self.memory.get("streak", 0) + 1
            self.memory["last_session"] = datetime.now().isoformat()
            self.save()
            return True
        else:
            # Streak broken, start over
            self.memory["streak"] = 1
            self.memory["last_session"] = datetime.now().isoformat()
            self.save()
            return False
    
    def add_message(self):
        """Record a message was sent."""
        self.memory["total_messages"] = self.memory.get("total_messages", 0) + 1
        self.memory["total_sessions"] = self.memory.get("total_sessions", 0) + 1
        self.memory["last_session"] = datetime.now().isoformat()
        self.save()
    
    def complete_scenario(self, scenario_id: str):
        """Mark a scenario as completed."""
        if scenario_id not in self.memory["completed_scenarios"]:
            self.memory["completed_scenarios"].append(scenario_id)
            self.save()
    
    def add_achievement(self, achievement_id: str):
        """Unlock an achievement."""
        if achievement_id not in self.memory["achievements"]:
            self.memory["achievements"].append(achievement_id)
            self.save()
            return True  # New achievement!
        return False
    
    def add_personal_note(self, note: str):
        """Add something personal Vera should remember."""
        self.memory["personal_notes"].append({
            "note": note,
            "added_at": datetime.now().isoformat(),
        })
        self.save()
    
    def get_summary(self) -> str:
        """Get a summary of user's progress for Vera to reference."""
        name = self.memory.get("name")
        level = self.memory.get("level", "A1")
        xp = self.memory.get("xp", 0)
        streak = self.memory.get("streak", 0)
        total_messages = self.memory.get("total_messages", 0)
        completed = len(self.memory.get("completed_scenarios", []))
        
        summary_parts = []
        if name:
            summary_parts.append(f"Användarens namn: {name}")
        summary_parts.append(f"Nivå: {level}")
        summary_parts.append(f"XP: {xp}")
        if streak > 1:
            summary_parts.append(f"Streak: {streak} dagar")
        if total_messages > 10:
            summary_parts.append(f"Totalt meddelanden: {total_messages}")
        if completed > 0:
            summary_parts.append(f"Avslutade lektioner: {completed}")
        
        return ", ".join(summary_parts) if summary_parts else "Ny användare"


# ============================================================================
# ACHIEVEMENTS SYSTEM — Celebrate Milestones
# ============================================================================

ACHIEVEMENTS = {
    "first_step": {
        "id": "first_step",
        "name_sv": "Första steget",
        "description_sv": "Skicka ditt första meddelande på svenska",
        "xp_reward": 10,
        "condition": lambda m: m.get("total_messages", 0) >= 1,
    },
    "fika_master": {
        "id": "fika_master",
        "name_sv": "Fika Master",
        "description_sv": "Slutför fika-lektionen",
        "xp_reward": 50,
        "condition": lambda m: "fika" in m.get("completed_scenarios", []),
    },
    "grocery_expert": {
        "id": "grocery_expert",
        "name_sv": "Matvaruexpert",
        "description_sv": "Slutför matvarulektionen",
        "xp_reward": 50,
        "condition": lambda m: "grocery" in m.get("completed_scenarios", []),
    },
    "apartment_hunter": {
        "id": "apartment_hunter",
        "name_sv": "Lägenhetsjägaren",
        "description_sv": "Slutför lägenhetslektionen",
        "xp_reward": 50,
        "condition": lambda m: "apartment" in m.get("completed_scenarios", []),
    },
    "voice_pro": {
        "id": "voice_pro",
        "name_sv": "Röstproffs",
        "description_sv": "Skicka 10 röstmessagen",
        "xp_reward": 100,
        "condition": lambda m: m.get("voice_messages", 0) >= 10,
    },
    "week_streak": {
        "id": "week_streak",
        "name_sv": "Veckostreak",
        "description_sv": "Öva 7 dagar i rad",
        "xp_reward": 100,
        "condition": lambda m: m.get("streak", 0) >= 7,
    },
    "month_streak": {
        "id": "month_streak",
        "name_sv": "Månadsmästare",
        "description_sv": "Öva 30 dagar i rad",
        "xp_reward": 500,
        "condition": lambda m: m.get("streak", 0) >= 30,
    },
    "conversation_starter": {
        "id": "conversation_starter",
        "name_sv": "Samtalsstartaren",
        "description_sv": "Skicka 50 meddelanden",
        "xp_reward": 100,
        "condition": lambda m: m.get("total_messages", 0) >= 50,
    },
    "polyglot": {
        "id": "polyglot",
        "name_sv": "Polyglotten",
        "description_sv": "Nå nivå B1",
        "xp_reward": 200,
        "condition": lambda m: m.get("level") == "B1",
    },
}


# ============================================================================
# MOOD DETECTION — Emotional Intelligence
# ============================================================================

def detect_mood(text: str) -> str:
    """
    Detect user's emotional state from their message.
    
    Returns: 'happy', 'sad', 'tired', 'excited', 'neutral', 'frustrated'
    """
    text_lower = text.lower()
    
    # Happy/positive indicators
    if any(word in text_lower for word in ["bra", "bra", "tack", "tack", "roligt", "glad", "tack", "👍", "😊", "😄", "❤️"]):
        return "happy"
    
    # Sad/tired indicators
    if any(word in text_lower for word in ["trött", "ledsen", "svårt", "jobbigt", "inte", "kan inte", "😔", "😢", "😞"]):
        return "tired" if "trött" in text_lower else "sad"
    
    # Excited indicators
    if any(word in text_lower for word in ["jätte", "väldigt", "super", "!", "🎉", "🔥", "💪"]):
        return "excited"
    
    # Frustrated indicators
    if any(word in text_lower for word in ["förstår inte", "svårt", "hjälp", "???"]):
        return "frustrated"
    
    return "neutral"


def get_mood_response(mood: str) -> str:
    """Get Vera's empathetic response based on detected mood."""
    responses = {
        "happy": "Åh, vad roligt att höra! 😊 Din glädje smittar av sig!",
        "sad": "Åh nej, min kära vän... 💙 Vill du prata om det? Jag lyssnar.",
        "tired": "Åh, du låter trött. Ta det lugnt! Ska vi göra en enkel övning eller vill du bara vila?",
        "excited": "JAG BLIR SÅ GLAD AV DIN ENERGI! 🎉 Berätta mer!",
        "frustrated": "Ta det lugnt! Det är helt okej att göra misstag. Det är så vi lär oss! 💪 Jag hjälper dig.",
        "neutral": "Jag är här för dig! 😊",
    }
    return responses.get(mood, responses["neutral"])


# ============================================================================
# VERA CHARACTER CLASS — Enhanced with Soul
# ============================================================================

class Vera:
    """
    Vera character class for Swedish language learning conversations.
    
    Now with:
    - Full personality and backstory
    - User memory (remembers name, progress, preferences)
    - Mood detection (responds emotionally)
    - Achievement system (celebrates milestones)
    - Personal touches (shares her life stories)
    """
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: str = "qwen3.5-flash",
        scenario_id: Optional[str] = None,
    ):
        """
        Initialize Vera character.
        
        Args:
            user_id: Unique user identifier for memory (e.g., Telegram chat_id)
            system_prompt: Custom system prompt (uses default if None)
            model: LLM model to use (default: qwen3.5-flash)
            scenario_id: Optional scenario ID for lesson mode
        """
        self.user_id = user_id
        self.memory = UserMemory(user_id) if user_id else None
        
        # Use scenario prompt if provided, otherwise use default Vera prompt
        if scenario_id:
            scenario_prompt = get_scenario_prompt(scenario_id)
            if scenario_prompt:
                self.system_prompt = scenario_prompt
                self.scenario_mode = True
                self.scenario_id = scenario_id
            else:
                self.system_prompt = system_prompt or VERA_SYSTEM_PROMPT
                self.scenario_mode = False
                self.scenario_id = None
        else:
            self.system_prompt = system_prompt or VERA_SYSTEM_PROMPT
            self.scenario_mode = False
            self.scenario_id = None
        
        self.model = model
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Get API key
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY or QWEN_API_KEY environment variable is not set. "
                "Set it with: export DASHSCOPE_API_KEY=your_key_here"
            )
        
        # Track voice messages for achievements
        self.voice_message_count = 0
    
    def _build_contextual_prompt(self, user_message: str) -> str:
        """
        Build enhanced prompt with user context and mood.
        
        This makes Vera remember the user and respond emotionally.
        """
        context_parts = []
        
        # Add user memory context
        if self.memory:
            user_name = self.memory.get("name")
            user_level = self.memory.get("level", "A1")
            streak = self.memory.get("streak", 0)
            completed = len(self.memory.get("completed_scenarios", []))
            
            if user_name:
                context_parts.append(f"ANVÄNDARENS NAMN: {user_name}")
            
            context_parts.append(f"ANVÄNDARENS NIVÅ: {user_level}")
            
            if streak >= 7:
                context_parts.append(f"STREAK: {streak} dagar i rad! (Vera bör gratulera!)")
            
            if completed > 0:
                context_parts.append(f"AVSLUTADE LEKTIONER: {completed}")
            
            # Add personal notes
            personal_notes = self.memory.get("personal_notes", [])
            if personal_notes:
                notes_text = ", ".join([n.get("note", "") for n in personal_notes[-3:]])
                context_parts.append(f"PERSONLIGT OM ANVÄNDAREN: {notes_text}")
        
        # Detect mood
        mood = detect_mood(user_message)
        if mood != "neutral":
            context_parts.append(f"ANVÄNDARENS HUMÖR: {mood} (Vera bör svara med empati)")
            context_parts.append(f"EMPATHY RESPONSE: {get_mood_response(mood)}")
        
        if not context_parts:
            return user_message
        
        return f"""
{user_message}

---
CONTEXTE INFORMATION (för Vera att använda naturligt i samtalet):
{" | ".join(context_parts)}
---

Svara naturligt på svenska som Vera, använd denna information för att göra samtalet personligt!
"""
    
    def chat(self, user_message: str, is_voice: bool = False) -> dict:
        """
        Have a conversation with Vera.
        
        Args:
            user_message: The user's message in Swedish (or English)
            is_voice: If True, this was a voice message (for achievements)
        
        Returns:
            dict with response text, mood, achievements, and progress
        """
        from openai import OpenAI
        
        # Update memory
        if self.memory:
            self.memory.add_message()
            self.memory.update_streak()
            
            if is_voice:
                self.voice_message_count += 1
                current_voice = self.memory.get("voice_messages", 0) + 1
                self.memory.set("voice_messages", current_voice)
            
            # Add XP for engagement
            xp_gained = 5 if not is_voice else 10
            new_level = self.memory.add_xp(xp_gained)
        
        # Build contextual prompt
        contextual_message = self._build_contextual_prompt(user_message)
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": contextual_message})
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=0.8,  # More creative and personal
            )
            assistant_message = response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            print("Please refer to https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
            assistant_message = "Åh nej, något gick fel! Försök igen, min kära vän! 💙"
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        # Check for achievements
        new_achievements = []
        if self.memory:
            for achievement in ACHIEVEMENTS.values():
                if achievement["condition"](self.memory.memory):
                    if self.memory.add_achievement(achievement["id"]):
                        new_achievements.append(achievement)
                        # Add achievement XP
                        self.memory.add_xp(achievement["xp_reward"])
        
        result = {
            "text": assistant_message,
            "mood": detect_mood(user_message),
            "history_length": len(self.conversation_history),
            "achievements": new_achievements,
        }
        
        # Add progress info if memory exists
        if self.memory:
            result["xp"] = self.memory.get("xp", 0)
            result["level"] = self.memory.get("level", "A1")
            result["streak"] = self.memory.get("streak", 0)
        
        return result
    
    def reset(self):
        """Reset conversation history (but keep memory)."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def get_history(self):
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def get_memory(self):
        """Get user memory (for debugging/stats)."""
        if self.memory:
            return self.memory.memory
        return None
    
    def start_scenario(self, scenario_id: str) -> bool:
        """
        Start a scenario lesson.
        
        Args:
            scenario_id: ID of the scenario (fika, grocery, apartment)
        
        Returns:
            True if scenario started successfully, False otherwise
        """
        scenario_prompt = get_scenario_prompt(scenario_id)
        if not scenario_prompt:
            return False
        
        self.scenario_id = scenario_id
        self.scenario_mode = True
        self.system_prompt = scenario_prompt
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        return True
    
    def complete_scenario(self):
        """Mark current scenario as completed in memory."""
        if self.memory and self.scenario_id:
            self.memory.complete_scenario(self.scenario_id)
    
    def exit_scenario(self):
        """Exit scenario mode and return to regular Vera chat."""
        # Mark as completed before exiting
        self.complete_scenario()
        
        self.scenario_mode = False
        self.scenario_id = None
        self.system_prompt = VERA_SYSTEM_PROMPT
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def learn_user_name(self, name: str):
        """Vera learns the user's name."""
        if self.memory:
            self.memory.set("name", name)
    
    def add_personal_note(self, note: str):
        """Vera remembers something personal about the user."""
        if self.memory:
            self.memory.add_personal_note(note)


# ============================================================================
# MAIN — Interactive Demo
# ============================================================================

def main():
    """Interactive chat with Vera (command-line demo)."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chat with Vera - your Swedish language buddy")
    parser.add_argument("--voice", action="store_true", help="Enable voice output (TTS)")
    parser.add_argument("--output-dir", default=".", help="Directory for audio output")
    parser.add_argument("--scenario", choices=["fika", "grocery", "apartment"], help="Start with a specific scenario lesson")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    parser.add_argument("--user-id", type=str, default="demo_user", help="User ID for memory persistence")
    args = parser.parse_args()
    
    # List scenarios if requested
    if args.list_scenarios:
        print("\n📚 Available Scenario Lessons\n")
        print("=" * 60)
        for scenario in list_scenarios():
            print(f"\n☕ {scenario['title_sv']} ({scenario['title']})")
            print(f"   Level: {scenario['level']}")
            print(f"   {scenario['description']}")
        print("\n" + "=" * 60)
        print("\nUse --scenario <id> to start a lesson")
        print("Example: uv run src/characters/vera.py --scenario fika --voice\n")
        return
    
    print("🇸🇪 Hej! Jag är Vera, din svenska språkkompis.")
    print("💖 Nu med minne och personlighet!")
    
    # Initialize Vera with user memory
    vera = Vera(user_id=args.user_id, scenario_id=args.scenario)
    
    if args.scenario:
        scenario = get_scenario(args.scenario)
        if scenario:
            print(f"📖 Starting lesson: {scenario.title_sv}")
            print(f"   {scenario.description}")
            print(f"\n💡 Tips: Say 'exit' to leave scenario mode, 'scenarios' to see all lessons\n")
    else:
        print("Skriv 'quit' för att avsluta, 'reset' för att börja om.")
        print("Skriv 'stats' för att se din progress.\n")
    
    counter = 0
    os.makedirs(args.output_dir, exist_ok=True)
    
    while True:
        try:
            user_input = input("Du: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHejdå!")
            break
        
        if user_input.lower() in ["quit", "exit", "q"]:
            if vera.scenario_mode:
                vera.exit_scenario()
                print("Vera: Hejdå! Bra jobbat idag! Jag är stolt över dig! 👋")
            else:
                print("Vera: Hejdå! Ha det så bra! Kom tillbaka snart! 💙👋")
            break
        
        if user_input.lower() == "reset":
            vera.reset()
            print("Vera: Conversation reset! Hej igen! 😊\n")
            continue
        
        if user_input.lower() == "stats":
            memory = vera.get_memory()
            if memory:
                print("\n📊 DIN PROGRESS:")
                print(f"   Namn: {memory.get('name', 'Inte satt än')}")
                print(f"   Nivå: {memory.get('level', 'A1')}")
                print(f"   XP: {memory.get('xp', 0)}")
                print(f"   Streak: {memory.get('streak', 0)} dagar")
                print(f"   Totalt meddelanden: {memory.get('total_messages', 0)}")
                print(f"   Avslutade lektioner: {len(memory.get('completed_scenarios', []))}")
                print(f"   Achievement: {len(memory.get('achievements', []))} låsta")
                print()
            continue
        
        if user_input.lower() == "scenarios":
            print("\n📚 Available Scenario Lessons:")
            for scenario in list_scenarios():
                print(f"   • {scenario['id']}: {scenario['title_sv']}")
            print("\nType 'scenario <id>' to start (e.g., 'scenario fika')\n")
            continue
        
        # Handle scenario switching
        if user_input.lower().startswith("scenario "):
            scenario_id = user_input.split()[1]
            if vera.start_scenario(scenario_id):
                scenario = get_scenario(scenario_id)
                print(f"\n📖 Starting lesson: {scenario.title_sv}")
                print(f"   Say 'exit scenario' to return to free chat\n")
            else:
                print(f"Scenario '{scenario_id}' not found. Type 'scenarios' to see all.\n")
            continue
        
        if user_input.lower() == "exit scenario":
            vera.exit_scenario()
            print("Vera: Exiting scenario mode. Back to free chat! 😊\n")
            continue
        
        if not user_input:
            continue
        
        try:
            response = vera.chat(user_input, is_voice=False)
            print(f"Vera: {response['text']}\n")
            
            # Show achievements if unlocked
            if response.get("achievements"):
                print("🏆 NYA ACHIEVEMENTS!")
                for achievement in response["achievements"]:
                    print(f"   🎯 {achievement['name_sv']}: {achievement['description_sv']}")
                    print(f"   +{achievement['xp_reward']} XP!")
                print()
            
            # Show progress occasionally
            if response.get("xp") and response["xp"] % 50 == 0:
                print(f"📊 Progress: Nivå {response['level']} | {response['xp']} XP | {response['streak']} dagar streak\n")
            
            if args.voice:
                counter += 1
                output_file = os.path.join(args.output_dir, f"vera_response_{counter}.mp3")
                from src.tts.tts import text_to_speech
                result = text_to_speech(
                    text_input=response['text'],
                    output_file=output_file,
                    voice_id="JBFqnCBsd6RMkjVDRZzb",
                    model_id="eleven_multilingual_v2",
                )
                print(f"🔊 Audio saved to: {result['output']}\n")
                
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
