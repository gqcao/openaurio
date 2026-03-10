# /// script
# dependencies = [
#   "openai",
#   "requests",
#   "python-telegram-bot",
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
from typing import Dict, Optional

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

from src.characters.vera import Vera
from src.tts.tts import text_to_speech
from src.speech.speech_to_text import speech_to_text
from src.scenarios.lessons import list_scenarios, get_scenario

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Store user sessions (chat_id → Vera instance)
user_sessions: Dict[int, Vera] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    
    # Create new Vera session for this user
    user_sessions[chat_id] = Vera()
    
    welcome_message = (
        "🇸🇪 **Hej! Jag är Vera, din svenska språkkompis!**\n\n"
        "Jag hjälper dig att lära dig svenska genom naturliga samtal.\n\n"
        "**Kommandon:**\n"
        "/scenarios - Visa övningslägen\n"
        "/fika - Starta fika-lektion\n"
        "/grocery - Starta matvarulektion\n"
        "/apartment - Starta lägenhetslektion\n"
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
    
    message = "📚 **Tillgängliga Övningslägen**\n\n"
    for scenario in scenarios:
        message += (
            f"**/{scenario['id']}** - {scenario['title_sv']}\n"
            f"_{scenario['description']}_\n"
            f"Nivå: {scenario['level']}\n\n"
        )
    
    message += "\nSkicka /<scenario> för att starta en lektion!"
    
    await update.message.reply_text(message, parse_mode="Markdown")


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
    
    # Create or update Vera session with scenario
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Vera(scenario_id=scenario_id)
    else:
        user_sessions[chat_id].start_scenario(scenario_id)
    
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
        f"_Skriv /reset för att avsluta lektionen._"
    )
    
    await update.message.reply_text(intro_message, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command."""
    chat_id = update.effective_chat.id
    
    if chat_id in user_sessions:
        user_sessions[chat_id].reset()
        await update.message.reply_text(
            "🔄 Samtalet har återställts! Hej igen! 😊"
        )
    else:
        user_sessions[chat_id] = Vera()
        await update.message.reply_text("🇸🇪 Hej! Jag är Vera. Vad kan jag hjälpa dig med?")


async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle regular text messages."""
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    if not user_text:
        return
    
    # Skip if it's a command (handled separately)
    if user_text.startswith("/"):
        return
    
    # Get or create Vera session
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Vera()
    
    vera = user_sessions[chat_id]
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Get Vera's response
        response = vera.chat(user_text)
        vera_text = response["text"]
        
        # Send text response
        await update.message.reply_text(vera_text)
        
        # Generate and send voice response
        await send_voice_response(update, vera_text)
        
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
    
    # Get or create Vera session
    if chat_id not in user_sessions:
        user_sessions[chat_id] = Vera()
    
    vera = user_sessions[chat_id]
    
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
        
        # Get Vera's response
        response = vera.chat(user_text)
        vera_text = response["text"]
        
        # Send transcription (for user to verify)
        await update.message.reply_text(
            f"🎤 **Du sa:**\n_{user_text}_\n\n"
            f"**Jag svarar:**\n{vera_text}",
            parse_mode="Markdown",
        )
        
        # Generate and send voice response
        await send_voice_response(update, vera_text)
        
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
    try:
        # Create temp file for TTS output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        # Generate TTS
        logger.info(f"Generating TTS for: {text[:50]}...")
        result = text_to_speech(
            text_input=text,
            output_file=temp_audio_path,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # Vera's voice (Rachel)
            model_id="eleven_multilingual_v2",
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
