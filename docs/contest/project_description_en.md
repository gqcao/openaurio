# openaurio - Language Buddy with a Soul

## One-Liner

**openaurio is an AI language learning companion with a soul, helping immigrants learn Swedish through emotional connection and personalized conversations.**

---

## Background

In Sweden, tens of thousands of immigrants wait months for SFI (Swedish for Immigrants) courses. During the waiting period, they lack opportunities for language practice. Traditional language learning apps (like Duolingo) are feature-rich but lack emotional connection, resulting in low user retention (<10%).

**Core Pain Points:**
- 📋 SFI waiting lists span several months
- 🤖 Traditional AI apps lack "human touch"
- 💔 Users lack emotional connection and easily give up
- 🗣️ Speaking practice opportunities are scarce

---

## Solution: Vera

**Vera is a 62-year-old retired Swedish teacher living in Gothenburg. She doesn't just teach you language—she cares about your life.**

### Key Features

**1. 🎭 Character with Soul**
- Complete personality: 62-year-old retired teacher with a cat, a garden, and stories
- Emotional intelligence: Detects user mood and responds with empathy
- Personal memory: Remembers user's name, progress, and life stories

**2. 🗣️ Voice Conversation**
- Speech-to-Text: User sends voice, Vera transcribes and understands
- Text-to-Speech: Vera responds with a warm Swedish voice
- Real speaking practice: Not multiple choice—actual conversation

**3. 📚 Scenario-Based Learning**
- ☕ **Fika Scenario**: Ordering at a café
- 🛒 **Grocery Scenario**: Shopping at a supermarket
- 🏠 **Apartment Scenario**: Asking about apartment rentals
- Each scenario includes cultural tips and key phrases

**4. 🎮 Gamification with Heart**
- XP points and level system (A1→A2→B1→B2)
- Daily streak tracking
- 9 achievement badges
- Progress visualization

**5. 🇸🇪 SFI Curriculum Aligned**
- Content aligned with official Swedish SFI curriculum
- Covers A1 to B1 levels
- Perfect for pre-SFI practice during waiting periods

---

## Technical Implementation

| Component | Technology |
|-----------|------------|
| AI Model | Qwen 3.5 Flash (via DashScope) |
| Speech Synthesis | ElevenLabs Multilingual v2 |
| Speech Recognition | Qwen ASR |
| User Interface | Telegram Bot |
| Memory System | JSON file storage |

---

## Innovation Points

1. **"Soul" over "Features"** — Not more features, but deeper connection
2. **Emotional Intelligence** — AI detects user mood and adjusts responses
3. **Character Consistency** — Vera has her own life, stories, and hobbies
4. **Voice-First** — Emphasizes speaking practice over multiple choice
5. **Social Impact** — Helps immigrants integrate into Swedish society

---

## Real-World Value

### User Value
- 📈 Improved language learning efficiency
- 💖 Emotional connection increases retention
- 🗣️ Real speaking practice opportunities
- 🇸🇪 Better integration into Swedish society

### Social Value
- 🏫 Reduces pressure on SFI schools
- 🤝 Promotes immigrant social integration
- 📚 Lowers language learning barriers
- 🌍 Scalable to other languages

---

## Demo Showcase

### Text Conversation
```
User: Hej Vera!
Vera: Hej [User]! Hur mår du idag? 😊

User: Jag är lite trött
Vera: Åh nej, min kära vän... 💙 Vill du prata om det? 
       Eller ska vi ta det lugnt idag?
```

### Voice Conversation
```
User: [Sends voice] "Jag vill ha en kanelbulle"
Vera: 🎤 You said: "Jag vill ha en kanelbulle"
       [Sends voice] "Åh, bra val! Kanelbullar är min favorit också!"
```

### Scenario Learning
```
User: /fika
Vera: 📖 Beställa fika
      Välkommen till kaféet! Vad kan jag hjälpa dig med?
      
User: Jag skulle vilja ha en kaffe
Vera: Ett kaffe, jättebra! Vill du ha något att äta också?
```

### Progress Tracking
```
User: /stats
Vera: 📊 Din Progress, [User]!
      
      Nivå: A2
      [████████░░] 150 XP
      
      🔥 Streak: 7 dagar
      💬 Totalt meddelanden: 45
      ✅ Avslutade lektioner: 2/3
      🏆 Achievements: 3 låsta
```

---

## Future Roadmap

### Short-term (1-3 months)
- [ ] Pilot partnership with Gothenburg SFI schools
- [ ] Add more scenarios (restaurant, hospital, bank)
- [ ] Improve speech recognition accuracy

### Mid-term (3-6 months)
- [ ] Develop Web interface
- [ ] Add more characters (Lars, Emma)
- [ ] Support other languages (English, German)

### Long-term (6-12 months)
- [ ] B2B version (corporate Swedish training)
- [ ] Partnership with Swedish Migration Agency
- [ ] Expand to other European countries

---

## Team Information

**Developer:** George Cao
**Location:** Gothenburg, Sweden
**GitHub:** https://github.com/gqcao/openaurio
**Demo:** https://t.me/vera_auriobot

---

## Acknowledgments

Special thanks to:
- OpenClaw team for the lobster framework
- Qwen/DashScope for AI model support
- ElevenLabs for speech synthesis

---

*"To learn a language, you need a friend. Vera is here for you. 🇸🇪"*