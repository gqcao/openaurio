# openaurio 🇸🇪

**Language buddy with a soul**

openaurio is an AI-powered language learning app focused on **personality-driven immersion**. Starting with Swedish for immigrants (SFI) in Gothenburg.

## Vision

> "Duolingo with personality" — learn languages through emotional connection with AI characters, not robotic drills.

## Core Features (POC)

- 🤖 **AI Character "Vera"** — your Swedish neighbor
- 🎙️ **Voice conversations** — speak and listen in Swedish
- 🔍 **Cultural context** — understand *why*, not just *what*
- 📈 **SFI-aligned progress** — track toward official levels

## Demo
![demo_swe](docs/demo_swe.gif)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python (FastAPI) |
| AI/TTS | Qwen 3.5 Flash |
| Speech-to-Text | Qwen ASR |
| Web Search | DuckDuckGo / LangSearch |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
export QWEN_API_KEY="your-key"

# Run TTS example
python src/tts/tts.py --text "Hej! Jag är Vera." --output hello.mp3
```

## Project Structure

```
openaurio/
├── src/
│   ├── tts/              # Text-to-speech (Swedish voice)
│   ├── speech/           # Speech-to-text (ASR)
│   ├── web_search/       # Web search for cultural info
│   └── characters/       # AI character definitions
├── docs/                 # Documentation
├── tests/                # Test suite
└── README.md
```

## Roadmap

- [x] TTS integration (Swedish)
- [x] ASR integration
- [ ] Character system (Vera)
- [ ] Chat interface
- [ ] SFI curriculum alignment
- [ ] Demo to SFI Göteborg

## License

MIT — Open source for the language learning community.

---

*Built with ❤️ in Gothenburg, Sweden*
