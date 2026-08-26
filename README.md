# MatNoble-TTS Agent Skill 🎙️

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-8A2BE2.svg)](https://github.com/MatNoble/matnoble-tts-skill)
[![Service](https://img.shields.io/badge/TTS_API-Online-success.svg)](https://speak.matnoble.top)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **MatNoble-TTS Agent Skill** 是专为现代 AI 智能体（**Claude Code**、**Google Antigravity**、**Cursor**、**Cline**、**OpenHands** 等）打造的高拟真文本转语音（TTS）与智能文稿润色技能。

本技能通过连接部署在 Cloudflare 边缘的 **[MatNoble-TTS 平台](https://speak.matnoble.top)**，赋予 AI Agent 强大的文稿修饰、语音指令注入（停顿/语速/重音/分词）、复杂男女声对诵 SSML 编排以及直接合成高品质 MP3 音频的能力。

---

## ⚡ 快速安装 (Installation)

### 方式 1：使用 `npx skills` 一键添加（推荐）
```bash
npx skills add MatNoble/matnoble-tts-skill
```

### 方式 2：使用 Git 直接克隆到本地 Agent 技能目录
```bash
# 适用于 Antigravity / Claude Code / 通用 Agent
mkdir -p ~/.agents/skills
git clone https://github.com/MatNoble/matnoble-tts-skill.git ~/.agents/skills/matnoble-tts
```

### 方式 3：从官方服务一键拉取打包产物
```bash
curl -fsSL https://speak.matnoble.top/skill.zip -o /tmp/tts-skill.zip && \
mkdir -p ~/.agents/skills/matnoble-tts && \
unzip -q /tmp/tts-skill.zip -d ~/.agents/skills/matnoble-tts && \
rm /tmp/tts-skill.zip
```

---

## 🌟 核心能力 (Key Features)

1. **智能文稿修饰与指令注入**：
   - 自动识别段落呼吸感，在合适位置注入 `[pause:500ms]` 停顿指令；
   - 注入情绪与语气强调（`[emphasis:strong]`、`[rate:slow]`、`[pitch:+15%]`、`[volume:loud]`）；
   - 智能识别电话、年月日、金额数字，应用 `[say-as:telephone]`、`[say-as:digits]`；
   - 专有名词/多音字音标纠正（`[sub:北京]bj[/sub]`）。
2. **专业级 SSML 对诵与播客生成**：
   - 具备完整的双人深情诗歌对诵（如《致橡树》）、多角色科技播客 XML 生成规范；
   - 支持跨语种与跨音色自然穿插。
3. **本地 Python 客户端工具**：
   - 内置 `scripts/tts_client.py`，AI Agent 可直接在命令行运行生成本地音频：
     ```bash
     python3 scripts/tts_client.py --text "大家好，欢迎收听我的播客！" --voice "zh-CN-YunxiNeural" --output podcast.mp3
     ```

---

## 🔌 开放 REST API 规范 (API Quickstart)

本平台提供标准符合 OpenAI 音频规范的高性能边缘 HTTP API，无需部署，开箱即用：

- **官方服务基址**：`https://speak.matnoble.top`
- **鉴权方式**：
  - 支持 **公共免 Key 体验通道**（单次 ≤ 500 字，每日公共共享额度）；
  - 配置专属 Key：请求头添加 `Authorization: Bearer vc_your_api_key`。

### 1. 文字转语音 (TTS)
- **端点**：`POST https://speak.matnoble.top/v1/audio/speech`
- **Content-Type**：`application/json`

#### cURL 示例：
```bash
curl -X POST "https://speak.matnoble.top/v1/audio/speech" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "大家好！欢迎使用 MatNoble-TTS 语音合成服务。[pause:500ms]祝大家创作愉快！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "speed": 1.0,
    "pitch": "0"
  }' \
  --output output.mp3
```

#### Python 示例：
```python
import requests

url = "https://speak.matnoble.top/v1/audio/speech"
headers = {
    "Authorization": "Bearer YOUR_API_KEY", # 留空使用公共通道
    "Content-Type": "application/json"
}
payload = {
    "input": "这是由 AI Agent 自动生成的语音音频。",
    "voice": "zh-CN-YunxiNeural",
    "speed": 1.0
}

response = requests.post(url, headers=headers, json=payload)
if response.status_code == 200:
    with open("speech.mp3", "wb") as f:
        f.write(response.content)
    print("音频生成成功：speech.mp3")
else:
    print(f"生成失败：{response.text}")
```

#### Node.js 示例：
```javascript
import fs from 'node:fs';

const response = await fetch("https://speak.matnoble.top/v1/audio/speech", {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    input: "Hello! Welcome to MatNoble-TTS AI voice platform.",
    voice: "en-US-JennyNeural",
    speed: 1.0
  })
});

if (response.ok) {
  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync("output.mp3", buffer);
  console.log("Audio saved to output.mp3");
}
```

### 2. SSML 复杂多角色合成
```json
{
  "format": "ssml",
  "ssml": "<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice name="zh-CN-XiaoxiaoNeural">晓晓说的第一句。<break time="500ms"/></voice><voice name="zh-CN-YunxiNeural">云希接着回应。</voice></speak>"
}
```

---

## 📁 目录结构 (Directory Structure)

```
matnoble-tts-skill/
├── SKILL.md                  # Agent Skill 主入口与系统提示词规范
├── README.md                 # 项目详细介绍与 API 开发者指南
├── package.json              # Skill 元数据说明
├── references/               # 深度参考手册
│   ├── api_reference.md      # REST API 端点、状态码与错误流控规范
│   ├── directives.md         # 语音指令语法与边界限制
│   ├── scriptwriting.md      # 播客、解说、对诵文稿创作方法论
│   ├── ssml_templates.md     # 微软 TTS SSML 高阶模板库
│   └── voices.md             # 26 款官方神经语音角色音色定位表
└── scripts/
    └── tts_client.py         # 命令行客户端与音频合成工具
```

---

## 📄 授权协议 (License)

本项目采用 [MIT License](LICENSE) 许可开源。
服务由 [MatNoble](https://matnoble.top) 维护，欢迎访问主页或提交 Issue 交流！
