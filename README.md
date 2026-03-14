# openaurio 🇸🇪

**Language buddy with a soul**

openaurio is an AI-powered language learning app focused on **personality-driven immersion**. Starting with Swedish for immigrants (SFI) in Gothenburg.

## Vision

> "Duolingo with personality" — learn languages through emotional connection with AI characters, not robotic drills.

## Demo

Try the Telegram bot: **[@vera_auriobot](https://t.me/vera_auriobot)**

<img src="docs/demo_swe.gif" alt="demo_swe" width="210" height="466">

## Core Features

- 🤖 **AI Character "Vera"** — 62-year-old Swedish neighbor with warm personality
- 🎙️ **Voice conversations** — speak and listen in Swedish (TTS + ASR)
- 🌤️ **Weather integration** — ask about weather in Swedish
- 🔍 **Web search** — search for news and cultural info
- 📈 **Progress tracking** — XP, levels, achievements, streaks
- 💙 **Mood detection** — Vera responds to your emotional state
- 📚 **Scenario lessons** — fika, grocery shopping, apartment hunting

## Tech Stack

| Component | Technology |
|-----------|------------|
| Interface | Telegram Bot |
| LLM | Google Gemini 2.5 Flash |
| TTS | ElevenLabs (Swedish voice) |
| Speech-to-Text | Qwen ASR (DashScope) |
| Web Search | DuckDuckGo (ddgs) |
| Weather | wttr.in |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/gqcao/openaurio.git
cd openaurio

# Install dependencies
uv pip install -r requirements.txt

# Create .env file with your API keys
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
GEMINI_API_KEY=your-gemini-api-key
ELEVEN_API_KEY=your-elevenlabs-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key
EOF

# Run the Telegram bot
uv run python src/bots/telegram_bot.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message (learns your name) |
| `/stats` | Show progress (XP, level, streak, achievements) |
| `/scenarios` | List all available lessons |
| `/fika` | Start fika scenario lesson |
| `/grocery` | Start grocery shopping lesson |
| `/apartment` | Start apartment hunting lesson |
| `/reset` | Reset conversation |
| `/help` | Show help |

## Project Structure

```
openaurio/
├── src/
│   ├── bots/
│   │   └── telegram_bot.py    # Main Telegram bot
│   ├── characters/
│   │   └── buddy.py           # Vera character + Gemini integration
│   ├── tts/
│   │   └── tts.py             # Text-to-speech (ElevenLabs)
│   ├── speech/
│   │   └── speech_to_text.py   # Speech-to-text (Qwen ASR)
│   ├── web_search/
│   │   └── web_search.py       # Web search (DuckDuckGo)
│   └── weather/
│       └── weather.py          # Weather (wttr.in)
├── docs/
│   └── contest/               # Contest submission materials
├── .env                       # API keys (not in git)
└── README.md
```

## Roadmap

- [x] TTS integration (Swedish voice)
- [x] ASR integration (voice input)
- [x] Character system (Vera)
- [x] Telegram bot interface
- [x] Weather & web search tools
- [x] Progress tracking (XP, levels, achievements)
- [x] Mood detection
- [x] Scenario lessons (fika, grocery, apartment)
- [ ] SFI curriculum alignment
- [ ] Demo to SFI schools in Gothenburg
- [ ] More characters (Lars, Emma)
- [ ] More scenarios (restaurant, pharmacy)

## License

MIT — Open source for the language learning community.

---

*Built with ❤️ in Gothenburg, Sweden*