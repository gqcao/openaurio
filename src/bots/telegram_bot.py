# /// script
# dependencies = [
#   "openai",
#   "requests",
#   "python-telegram-bot",
#   "python-dotenv",
# ]
# ///

"""
openaurio Telegram Bot

Vera - Your Swedish Language Buddy on Telegram
Supports text and voice messages, scenario lessons, and TTS responses.
"""

import sys
import os
import tempfile
import logging
import time
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
# Add project root to path so 'src' module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.characters import Buddy
from src.tts.tts import text_to_speech
from src.speech.speech_to_text import speech_to_text
from src.scenarios.lessons import list_scenarios, get_scenario
from src.analytics import FeedbackLogger, ConversationLogger

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Store user sessions (chat_id → Buddy instance)
user_sessions: Dict[int, Buddy] = {}

# Track scenario completion (to award achievements)
user_scenarios_in_progress: Dict[int, str] = {}

# Initialize analytics
feedback_logger = FeedbackLogger()
conversation_logger = ConversationLogger()

# ============================================================================
# RATE LIMITING
# ============================================================================

# Rate limit settings
RATE_LIMIT_MAX_MESSAGES = 50  # Max messages per hour per user. Set to -1 for unlimited.
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour window
RATE_LIMIT_DAILY = 300  # Max messages per day per user. Set to -1 for unlimited.
MIN_MESSAGE_INTERVAL = 2  # Minimum seconds between messages. Set to 0 to disable.

# Track user message timestamps for rate limiting
# Format: {chat_id: [timestamp1, timestamp2, ...]}
user_message_times: Dict[int, List[float]] = {}

# Track daily message counts: {chat_id: {"date": "YYYY-MM-DD", "count": int}}
user_daily_counts: Dict[int, Dict] = {}

# Track last message time for cooldown: {chat_id: last_timestamp}
user_last_message: Dict[int, float] = {}


def check_rate_limit(chat_id: int) -> tuple[bool, str]:
    """
    Check if user is within rate limits.
    
    Returns:
        (is_allowed, message) - is_allowed is True if user can send message
    """
    current_time = time.time()
    current_date = time.strftime("%Y-%m-%d")
    
    # === Check minimum message interval (cooldown) ===
    if MIN_MESSAGE_INTERVAL > 0:
        if chat_id in user_last_message:
            time_since_last = current_time - user_last_message[chat_id]
            if time_since_last < MIN_MESSAGE_INTERVAL:
                wait_seconds = int(MIN_MESSAGE_INTERVAL - time_since_last)
                return False, f"⏳ Vänta {wait_seconds} sekunder innan du skickar nästa meddelande."
    
    # === Check hourly rate limit ===
    if RATE_LIMIT_MAX_MESSAGES > 0:
        if chat_id not in user_message_times:
            user_message_times[chat_id] = []
        
        # Remove old timestamps outside the window
        user_message_times[chat_id] = [
            t for t in user_message_times[chat_id]
            if current_time - t < RATE_LIMIT_WINDOW_SECONDS
        ]
        
        # Check if user has hit the hourly limit
        if len(user_message_times[chat_id]) >= RATE_LIMIT_MAX_MESSAGES:
            oldest_in_window = min(user_message_times[chat_id])
            time_until_reset = RATE_LIMIT_WINDOW_SECONDS - (current_time - oldest_in_window)
            minutes_left = int(time_until_reset / 60) + 1
            
            return False, f"⏳ Du har nått din gräns på {RATE_LIMIT_MAX_MESSAGES} meddelanden i timmen! Vänta {minutes_left} minuter till nästa timme."
    
    # === Check daily rate limit ===
    if RATE_LIMIT_DAILY > 0:
        if chat_id not in user_daily_counts:
            user_daily_counts[chat_id] = {"date": current_date, "count": 0}
        
        # Reset count if it's a new day
        if user_daily_counts[chat_id]["date"] != current_date:
            user_daily_counts[chat_id] = {"date": current_date, "count": 0}
        
        # Check if user has hit the daily limit
        if user_daily_counts[chat_id]["count"] >= RATE_LIMIT_DAILY:
            return False, f"🛑 Du har nått din dagliga gräns på {RATE_LIMIT_DAILY} meddelanden! Kom tillbaka imorgon."
        
        # Increment daily count
        user_daily_counts[chat_id]["count"] += 1
    
    # === Record this message ===
    if RATE_LIMIT_MAX_MESSAGES > 0:
        user_message_times[chat_id].append(current_time)
    
    user_last_message[chat_id] = current_time
    
    return True, ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "min vän"
    
    # Create new Buddy session for this user with memory
    user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
    
    # Learn user's name
    user_sessions[chat_id].learn_user_name(user_name)
    
    welcome_message = (
        f"🇸🇪 **Hej {user_name}! Jag är Vera, din svenska språkkompis!** 💖\n\n"
        "Jag är en 62-årig pensionerad lärarinna som bor i Göteborg.\n"
        "Jag älskar att baka kanbullar, min katt Misse, och att hjälpa dig lära dig svenska! 🏡🐱\n\n"
        "**Vad jag kan göra:**\n"
        "• Prata svenska med dig (text eller röst)\n"
        "• Lärande genom naturliga samtal\n"
        "• 3 övningslägen (fika, matbutik, lägenhet)\n"
        "• Jag kommer ihåg dig och din progress!\n\n"
        "**Kommandon:**\n"
        "/scenarios - Visa övningslägen\n"
        "/fika - Starta fika-lektion ☕\n"
        "/grocery - Starta matvarulektion 🛒\n"
        "/apartment - Starta lägenhetslektion 🏠\n"
        "/stats - Visa din progress 📊\n"
        "/feedback - Ge feedback 💬\n"
        "/reset - Återställ samtal\n"
        "/help - Visa hjälp\n\n"
        "Skicka text eller röstmessagen på svenska så svarar jag! 😊"
    )
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📚 **Hjälp - Hur använder du Vera**\n\n"
        "**Grundläggande:**\n"
        "- Skicka textmeddelanden på svenska\n"
        "- Skicka röstmessagen (håll in mikrofonen)\n"
        "- Jag svarar med text och ljud\n\n"
        "**Övningslägen:**\n"
        "- /scenarios - Visa alla lektioner\n"
        "- /fika - Öva på kafé\n"
        "- /grocery - Öva i matbutiken\n"
        "- /apartment - Öva lägenhetssökning\n\n"
        "**Andra kommandon:**\n"
        "- /reset - Starta om samtal\n"
        "- /start - Välkomstmeddelande\n\n"
        "Lycka till med svenskan! 🇸🇪"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def scenarios_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /scenarios command."""
    scenarios = list_scenarios()
    
    message = "📚 Tillgängliga Övningslägen\n\n"
    for scenario in scenarios:
        message += (
            f"• /{scenario['id']} — {scenario['title_sv']}\n"
            f"  {scenario['description']}\n"
            f"  Nivå: {scenario['level']}\n\n"
        )
    
    message += "Skicka /<scenario> för att starta en lektion!"
    
    await update.message.reply_text(message)


async def scenario_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    scenario_id: str,
):
    """Handle scenario commands (/fika, /grocery, /apartment)."""
    chat_id = update.effective_chat.id
    
    scenario = get_scenario(scenario_id)
    if not scenario:
        await update.message.reply_text(
            f"❌ Lektionen '{scenario_id}' hittades inte.\n"
            f"Använd /scenarios för att se alla lägen."
        )
        return
    
    # Create or update Buddy session with scenario
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id), scenario_id=scenario_id)
    else:
        user_sessions[chat_id].start_scenario(scenario_id)
    
    # Track that user is in this scenario
    user_scenarios_in_progress[chat_id] = scenario_id
    
    intro_message = (
        f"📖 **{scenario.title_sv}**\n\n"
        f"{scenario.description_sv}\n\n"
        f"💡 **Kulturella tips:**\n"
    )
    
    for i, tip in enumerate(scenario.cultural_tips[:3], 1):
        intro_message += f"{i}. {tip}\n"
    
    intro_message += "\n🗣️ **Nyckelord:**\n"
    for phrase in scenario.key_phrases[:3]:
        intro_message += f"• {phrase['svenska']}\n"
    
    intro_message += (
        f"\n\n**Nu börjar vi!** Skriv eller prata på svenska så svarar jag. 😊\n"
        f"_När du är klar, skriv 'tack' eller 'klar' så avslutar vi lektionen._\n"
        f"_Skriv /reset för att avsluta direkt._"
    )
    
    await update.message.reply_text(intro_message, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show user progress."""
    chat_id = update.effective_chat.id
    
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
    
    buddy = user_sessions[chat_id]
    memory = buddy.get_memory()
    
    if not memory:
        await update.message.reply_text("❌ Ingen progress hittades än.")
        return
    
    name = memory.get("name", "Okänd")
    level = memory.get("level", "A1")
    xp = memory.get("xp", 0)
    streak = memory.get("streak", 0)
    total_messages = memory.get("total_messages", 0)
    completed = len(memory.get("completed_scenarios", []))
    achievements = len(memory.get("achievements", []))
    
    # Level progress bar
    next_level_xp = 100 if level == "A1" else 300 if level == "A2" else 600 if level == "B1" else 1000
    prev_level_xp = 0 if level == "A1" else 100 if level == "A2" else 300 if level == "B1" else 600
    progress = ((xp - prev_level_xp) / (next_level_xp - prev_level_xp)) * 100
    progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
    
    stats_message = (
        f"📊 **Din Progress, {name}!**\n\n"
        f"**Nivå:** {level}\n"
        f"[{progress_bar}] {xp} XP\n\n"
        f"**🔥 Streak:** {streak} dagar\n"
        f"**💬 Totalt meddelanden:** {total_messages}\n"
        f"**✅ Avslutade lektioner:** {completed}/3\n"
        f"**🏆 Achievements:** {achievements} låsta\n\n"
        f"_Fortsätt så här så blir du flytande i svenska!_ 💪🇸🇪"
    )
    
    await update.message.reply_text(stats_message, parse_mode="Markdown")


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /feedback command - collect user feedback."""
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "min vän"
    
    # Get feedback text from command arguments
    feedback_text = " ".join(context.args) if context.args else None
    
    if not feedback_text:
        # No feedback provided, show instructions
        await update.message.reply_text(
            "📝 **Feedback**\n\n"
            "Jag vill gärna höra dina tankar! Skriv:\n\n"
            "`/feedback Din feedback här`\n\n"
            "Exempel:\n"
            "• `/feedback Vera pratar för fort`\n"
            "• `/feedback Jag vill ha fler lektioner`\n"
            "• `/feedback Älskar appen! 💖`\n\n"
            "_All feedback hjälper mig bli bättre!_",
            parse_mode="Markdown",
        )
        return
    
    # Get user info
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
    
    buddy = user_sessions[chat_id]
    memory = buddy.get_memory() or {}
    
    # Log feedback
    success = feedback_logger.log_feedback(
        user_id=str(chat_id),
        user_name=user_name,
        feedback_text=feedback_text,
        level=memory.get("level", "A1"),
        xp=memory.get("xp", 0),
        scenario=user_scenarios_in_progress.get(chat_id),
    )
    
    if success:
        await update.message.reply_text(
            "✅ **Tack för din feedback!**\n\n"
            f"_\"{feedback_text}\"_\n\n"
            "Jag uppskattar att du tog dig tid att hjälpa mig bli bättre! 💖\n"
            "Din feedback hjälper mig att förbättra upplevelsen för alla.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "❌ Något gick fel med att spara din feedback. Försök igen senare."
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command."""
    chat_id = update.effective_chat.id
    
    if chat_id in user_sessions:
        user_sessions[chat_id].reset()
        await update.message.reply_text(
            "🔄 Samtalet har återställts! Hej igen! 😊"
        )
    else:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
        await update.message.reply_text("🇸🇪 Hej! Jag är Vera. Vad kan jag hjälpa dig med?")


async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle regular text messages."""
    chat_id = update.effective_chat.id
    user_text = update.message.text
    user_name = update.effective_chat.first_name or "min vän"
    
    if not user_text:
        return
    
    # Skip if it's a command (handled separately)
    if user_text.startswith("/"):
        return
    
    # Check rate limit
    is_allowed, rate_limit_msg = check_rate_limit(chat_id)
    if not is_allowed:
        await update.message.reply_text(rate_limit_msg)
        return
    
    # Get or create Buddy session
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
    
    buddy = user_sessions[chat_id]
    memory = buddy.get_memory() or {}
    
    # Check if user is completing a scenario
    if buddy.scenario_mode and user_text.lower() in ["tack", "klar", "tack för mig", "det var allt"]:
        scenario_id = user_scenarios_in_progress.get(chat_id)
        if scenario_id:
            buddy.exit_scenario()  # This marks scenario as completed
            del user_scenarios_in_progress[chat_id]
            
            scenario = get_scenario(scenario_id)
            await update.message.reply_text(
                f"🎉 **BRA JOBBAT!**\n\n"
                f"Du har avslutat **{scenario.title_sv}**!\n"
                f"+50 XP för att du slutförde lektionen!\n\n"
                f"Vill du fortsätta prata eller prova en annan lektion?\n"
                f"Använd /scenarios för att se alla lägen.",
                parse_mode="Markdown",
            )
            return
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Get Buddy's response
        response = buddy.chat(user_text, is_voice=False)
        buddy_text = response["text"]
        
        # Log conversation
        conversation_logger.log_conversation(
            user_id=str(chat_id),
            user_name=user_name,
            user_message=user_text,
            vera_response=buddy_text,
            is_voice=False,
            scenario=user_scenarios_in_progress.get(chat_id),
            level=memory.get("level", "A1"),
            xp=memory.get("xp", 0),
            achievements_unlocked=response.get("achievements", []),
        )
        
        # Send text response
        await update.message.reply_text(buddy_text)
        
        # Show achievements if unlocked
        if response.get("achievements"):
            achievement_text = "🏆 **NYA ACHIEVEMENTS!**\n\n"
            for achievement in response["achievements"]:
                achievement_text += (
                    f"🎯 **{achievement['name_sv']}**\n"
                    f"_{achievement['description_sv']}_\n"
                    f"+{achievement['xp_reward']} XP!\n\n"
                )
            await update.message.reply_text(achievement_text, parse_mode="Markdown")
        
        # Generate and send voice response
        await send_voice_response(update, buddy_text)
        
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        await update.message.reply_text(
            "❌ Oops! Något gick fel. Försök igen!"
        )


async def handle_voice_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle voice messages (audio)."""
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.first_name or "min vän"
    
    # Check rate limit
    is_allowed, rate_limit_msg = check_rate_limit(chat_id)
    if not is_allowed:
        await update.message.reply_text(rate_limit_msg)
        return
    
    # Get or create Buddy session
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Buddy(character_id="vera", user_id=str(chat_id))
    
    buddy = user_sessions[chat_id]
    memory = buddy.get_memory() or {}
    
    # Download voice message
    voice_file = await update.message.voice.get_file()
    
    # Create temp file for audio
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        await voice_file.download_to_drive(temp_audio_path)
    
    try:
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Transcribe audio
        logger.info(f"Transcribing audio: {temp_audio_path}")
        transcription = speech_to_text(temp_audio_path)
        user_text = transcription.get("text", "")
        
        if not user_text:
            await update.message.reply_text(
                "❌ Jag kunde inte höra vad du sa. Försök igen!"
            )
            return
        
        logger.info(f"Transcribed: {user_text}")
        
        # Get Buddy's response (mark as voice message for XP bonus)
        response = buddy.chat(user_text, is_voice=True)
        buddy_text = response["text"]
        
        # Log conversation
        conversation_logger.log_conversation(
            user_id=str(chat_id),
            user_name=user_name,
            user_message=user_text,
            vera_response=buddy_text,
            is_voice=True,
            scenario=user_scenarios_in_progress.get(chat_id),
            level=memory.get("level", "A1"),
            xp=memory.get("xp", 0),
            achievements_unlocked=response.get("achievements", []),
        )
        
        # Send transcription (for user to verify)
        await update.message.reply_text(
            f"🎤 **Du sa:**\n_{user_text}_\n\n"
            f"**Jag svarar:**\n{buddy_text}",
            parse_mode="Markdown",
        )
        
        # Show achievements if unlocked
        if response.get("achievements"):
            achievement_text = "🏆 **NYA ACHIEVEMENTS!**\n\n"
            for achievement in response["achievements"]:
                achievement_text += (
                    f"🎯 **{achievement['name_sv']}**\n"
                    f"_{achievement['description_sv']}_\n"
                    f"+{achievement['xp_reward']} XP!\n\n"
                )
            await update.message.reply_text(achievement_text, parse_mode="Markdown")
        
        # Generate and send voice response
        await send_voice_response(update, buddy_text)
        
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        await update.message.reply_text(
            "❌ Oops! Något gick fel med rösten. Försök igen!"
        )
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)


async def send_voice_response(update: Update, text: str):
    """Generate TTS audio and send as voice message."""
    # Skip TTS for very short responses - Gemini TTS model confuses
    # short conversational phrases (like "Hej!", "Åh!") as text prompts
    if len(text) < 30:
        logger.info(f"Skipping TTS for short text: {text[:30]}...")
        return
    
    try:
        # Create temp file for TTS output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        # Generate TTS
        logger.info(f"Generating TTS for: {text[:50]}...")
        result = text_to_speech(
            text_input=text,
            output_file=temp_audio_path,
            voice_name="Leda",  # Vera's voice (soft, gentle)
            model_id="gemini-2.5-flash-preview-tts",
        )
        
        # Send as voice message
        with open(temp_audio_path, "rb") as audio_file:
            await update.message.reply_voice(
                voice=audio_file,
                caption="🔊 Vera svarar",
            )
        
        # Clean up
        os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        # Still send text even if TTS fails
        await update.message.reply_text(
            "⚠️ (Ljudet kunde inte genereras, men här är texten ovan)"
        )


async def error_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")


def main():
    """Run the Telegram bot."""
    import argparse
    
    parser = argparse.ArgumentParser(description="openaurio Telegram Bot")
    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)",
    )
    args = parser.parse_args()
    
    if not args.token:
        print(
            "❌ Error: Telegram bot token not provided.\n"
            "Set it with:\n"
            "  export TELEGRAM_BOT_TOKEN=your_token_here\n"
            "Or run with:\n"
            "  uv run src/bots/telegram_bot.py --token YOUR_TOKEN"
        )
        sys.exit(1)
    
    print("🤖 Starting openaurio Telegram Bot...")
    print(f"🇸🇪 Vera is ready to help users learn Swedish!")
    print(f"\nBot username: @{args.token.split(':')[0].split('-')[0]} (check @BotFather)")
    print("\nPress Ctrl+C to stop.\n")
    
    # Build application
    application = Application.builder().token(args.token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("scenarios", scenarios_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Scenario commands
    application.add_handler(CommandHandler("fika", lambda u, c: scenario_command(u, c, "fika")))
    application.add_handler(CommandHandler("grocery", lambda u, c: scenario_command(u, c, "grocery")))
    application.add_handler(CommandHandler("apartment", lambda u, c: scenario_command(u, c, "apartment")))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
