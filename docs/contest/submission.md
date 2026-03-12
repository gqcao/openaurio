# openaurio - 首届中关村北纬龙虾大赛参赛作品

## 基本信息

**作品名称:** openaurio - Language Buddy with a Soul
**参赛赛道:** 生产力龙虾
**作品类型:** AI语言学习助手
**Demo链接:** https://t.me/vera_auriobot
**GitHub:** https://github.com/gqcao/openaurio

---

## 一句话介绍

**openaurio是一个有灵魂的AI语言学习伙伴，通过情感连接和个性化对话帮助移民学习瑞典语。**

---

## 作品描述

### 问题背景

在瑞典，每年有数万移民等待SFI（瑞典语作为第二语言）课程。等待期间，他们无法获得足够的语言练习机会。传统语言学习应用（如Duolingo）虽然功能强大，但缺乏情感连接，用户留存率低（<10%）。

**核心痛点：**
- 📋 SFI等待名单长达数月
- 🤖 传统AI应用缺乏"人情味"
- 💔 用户缺乏情感连接，容易放弃
- 🗣️ 口语练习机会稀缺

### 解决方案：Vera

**Vera是一位62岁的退休瑞典语老师，住在哥德堡。她不只是教你语言，她关心你的生活。**

#### 核心特性

**1. 🎭 有灵魂的角色 (Character with Soul)**
- 完整的人格设定：62岁退休老师，有猫、有花园、有故事
- 情绪智能：检测用户心情并给予情感回应
- 个人记忆：记住用户的名字、进度、生活故事

**2. 🗣️ 语音对话 (Voice Conversation)**
- 语音转文字 (STT)：用户发送语音，Vera转录并理解
- 文字转语音 (TTS)：Vera用温暖的瑞典语声音回复
- 真实口语练习：不是选择题，是真正的对话

**3. 📚 场景式学习 (Scenario Learning)**
- ☕ **Fika场景**：在咖啡馆点餐
- 🛒 **超市场景**：在超市购物
- 🏠 **租房场景**：询问公寓租赁
- 每个场景包含文化提示和关键短语

**4. 🎮 游戏化系统 (Gamification with Heart)**
- XP经验值和等级系统 (A1→A2→B1→B2)
- 连续学习天数追踪
- 9个成就徽章
- 进度可视化

**5. 🇸🇪 SFI课程对齐**
- 内容与瑞典官方SFI课程对齐
- 从A1到B1级别覆盖
- 适合SFI等待期间的预习

### 技术实现

| 组件 | 技术 |
|------|------|
| AI模型 | Qwen 3.5 Flash (via DashScope) |
| 语音合成 | ElevenLabs Multilingual v2 |
| 语音识别 | Qwen ASR |
| 用户界面 | Telegram Bot |
| 记忆系统 | JSON文件存储 |

### 创新点

1. **"灵魂"而非"功能"** - 不是更多功能，而是更深连接
2. **情绪智能** - AI能感知用户心情并调整回应
3. **角色一致性** - Vera有自己的生活、故事、爱好
4. **语音优先** - 强调口语练习而非选择题
5. **社会价值** - 帮助移民融入瑞典社会

---

## 实际价值

### 用户价值
- 📈 提高语言学习效率
- 💖 建立情感连接，提高留存率
- 🗣️ 获得真实口语练习机会
- 🇸🇪 更好地融入瑞典社会

### 社会价值
- 🏫 减轻SFI学校压力
- 🤝 促进移民社会融合
- 📚 降低语言学习门槛
- 🌍 可扩展到其他语言

---

## Demo展示

### 文字对话
```
用户: Hej Vera!
Vera: Hej [用户名]! Hur mår du idag? 😊

用户: Jag är lite trött
Vera: Åh nej, min kära vän... 💙 Vill du prata om det? 
      Eller ska vi ta det lugnt idag?
```

### 语音对话
```
用户: [发送语音] "Jag vill ha en kanelbulle"
Vera: 🎤 Du sa: "Jag vill ha en kanelbulle"
       [发送语音] "Åh, bra val! Kanelbullar är min favorit också!"
```

### 场景学习
```
用户: /fika
Vera: 📖 Beställa fika
      Välkommen till kaféet! Vad kan jag hjälpa dig med?
      
用户: Jag skulle vilja ha en kaffe
Vera: Ett kaffe, jättebra! Vill du ha något att äta också?
```

### 进度追踪
```
用户: /stats
Vera: 📊 Din Progress, [用户名]!
      
      Nivå: A2
      [████████░░] 150 XP
      
      🔥 Streak: 7 dagar
      💬 Totalt meddelanden: 45
      ✅ Avslutade lektioner: 2/3
      🏆 Achievements: 3 låsta
```

---

## 未来规划

### 短期 (1-3个月)
- [ ] 与哥德堡SFI学校合作试点
- [ ] 添加更多场景（餐厅、医院、银行）
- [ ] 改进语音识别准确率

### 中期 (3-6个月)
- [ ] 开发Web界面
- [ ] 添加更多角色（Lars, Emma）
- [ ] 支持其他语言（英语、德语）

### 长期 (6-12个月)
- [ ] B2B版本（企业瑞典语培训）
- [ ] 与瑞典移民局合作
- [ ] 扩展到其他欧洲国家

---

## 团队信息

**开发者:** [您的名字]
**地点:** 瑞典哥德堡
**联系方式:** [您的邮箱]
**GitHub:** https://github.com/gqcao/openaurio

---

## 致谢

感谢以下技术支持：
- OpenClaw团队提供的龙虾框架
- Qwen/DashScope提供的AI模型
- ElevenLabs提供的语音合成

---

*"学习语言，需要一个朋友。Vera在这里等你。🇸🇪"*