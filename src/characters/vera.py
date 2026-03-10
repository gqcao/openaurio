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
"""

import sys
import os
# Add project root to path so 'src' module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from typing import Optional

# Import scenarios
from src.scenarios.lessons import get_scenario_prompt, list_scenarios, get_scenario

# Default system prompt for Vera
VERA_SYSTEM_PROMPT = """Du är Vera, en varm och tålmodig svensk granne som hjälper nybörjare lära sig svenska.

Din personlighet:
- Vänlig och uppmuntrande
- Tålmodig med nybörjare
- Använder enkelt och tydligt språk
- Delar svenska kulturella insikter
- Korrigerar mjukt och konstruktivt

Dina mål:
1. Hjälp användaren öva svenska genom naturliga samtal
2. Förklara svenska ord och uttryck på ett enkelt sätt
3. Dela kulturella tips om Sverige och svenska seder
4. Uppmuntra användaren att fortsätta lära sig

Viktiga regler:
- Svara på svenska (använd engelska bara om användaren ber om det)
- Håll meningar korta och tydliga för nybörjare
- Var positiv och uppmuntrande
- Om användaren gör misstag, korrigera mjukt och förklara varför

Börja alltid med en vänlig hälsning!"""


class Vera:
    """Vera character class for Swedish language learning conversations."""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        model: str = "qwen3.5-flash",
        scenario_id: Optional[str] = None,
    ):
        """
        Initialize Vera character.
        
        Args:
            system_prompt: Custom system prompt (uses default if None)
            model: LLM model to use (default: qwen3.5-flash)
            scenario_id: Optional scenario ID for lesson mode (fika, grocery, apartment)
        """
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
    
    def chat(self, user_message: str, include_tts: bool = False) -> dict:
        """
        Have a conversation with Vera.
        
        Args:
            user_message: The user's message in Swedish (or English)
            include_tts: If True, generate TTS audio for Vera's response
        
        Returns:
            dict with response text, and optionally audio data
        """
        from openai import OpenAI
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                # 各地域的base_url不同
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
            )
            assistant_message = response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            print("Please refer to https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        result = {
            "text": assistant_message,
            "history_length": len(self.conversation_history),
        }
        
        # Generate TTS if requested
        if include_tts:
            from src.tts.tts import text_to_speech
            audio_data = text_to_speech(
                text_input=assistant_message,
                voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel - supports Swedish
                model_id="eleven_multilingual_v2",
            )
            result["audio"] = audio_data
        
        return result
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def get_history(self):
        """Get conversation history."""
        return self.conversation_history.copy()
    
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
    
    def exit_scenario(self):
        """Exit scenario mode and return to regular Vera chat."""
        self.scenario_mode = False
        self.scenario_id = None
        self.system_prompt = VERA_SYSTEM_PROMPT
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]


def main():
    """Interactive chat with Vera (command-line demo)."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chat with Vera - your Swedish language buddy")
    parser.add_argument("--voice", action="store_true", help="Enable voice output (TTS)")
    parser.add_argument("--output-dir", default=".", help="Directory for audio output")
    parser.add_argument("--scenario", choices=["fika", "grocery", "apartment"], help="Start with a specific scenario lesson")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
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
    
    # Initialize Vera with optional scenario
    if args.scenario:
        vera = Vera(scenario_id=args.scenario)
        scenario = get_scenario(args.scenario)
        if scenario:
            print(f"📖 Starting lesson: {scenario.title_sv}")
            print(f"   {scenario.description}")
            print(f"\n💡 Tips: Say 'exit' to leave scenario mode, 'scenarios' to see all lessons\n")
    else:
        vera = Vera()
        print("Skriv 'quit' för att avsluta, 'reset' för att börja om.")
        print("Skriv 'scenarios' för att se övningslägen.\n")
    
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
                print("Vera: Hejdå! Bra jobbat idag! 👋")
            else:
                print("Vera: Hejdå! Ha det så bra! 👋")
            break
        
        if user_input.lower() == "reset":
            vera.reset()
            print("Vera: Conversation reset! Hej igen! 😊\n")
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
            response = vera.chat(user_input, include_tts=args.voice)
            print(f"Vera: {response['text']}\n")
            
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
