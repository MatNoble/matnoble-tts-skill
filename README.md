# MatNoble-TTS Agent Skill 🎙️ (Director 2.0)

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-8A2BE2.svg)](https://github.com/MatNoble/matnoble-tts-skill)
[![Service](https://img.shields.io/badge/TTS_API-Online-success.svg)](https://speak.matnoble.top)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **MatNoble-TTS Agent Skill** 是专为现代 AI 智能体（**Claude Code**、**Google Antigravity**、**Cursor**、**Cline**、**OpenHands** 等）打造的**专业 AI 配音导演（Audio Director）与高拟真语音创作技能**。

本技能通过连接部署在 Cloudflare 边缘的 **[MatNoble-TTS 平台](https://speak.matnoble.top)**，赋予 AI Agent 识别文稿体裁、匹配黄金音色参数（Voice × Speed × Pitch × Style）、执行非标准词（NSW）规范化、多音字防翻车打标、四级韵律呼吸留白、复杂多角色 SSML 编排以及终端直接合成高品质 MP3 音频的全套能力。

---

## ⚡ 安装与更新 (Installation & Update)

### 1. 使用 `npx skills` 一键添加（推荐）
```bash
# 初次安装
npx skills add MatNoble/matnoble-tts-skill

# 版本更新（获取最新体裁蓝图、变调规则与多音字词典）
npx skills update MatNoble/matnoble-tts-skill
```

### 2. 使用 Git 直接克隆到本地 Agent 技能目录
```bash
# 适用于 Antigravity / Claude Code / 通用 Agent 技能目录
mkdir -p ~/.agents/skills
git clone https://github.com/MatNoble/matnoble-tts-skill.git ~/.agents/skills/matnoble-tts

# 更新只需在目录内拉取
cd ~/.agents/skills/matnoble-tts && git pull
```

### 3. 从官方部署站点一键拉取打包产物（免 GitHub 直连）
```bash
curl -fsSL https://speak.matnoble.top/skill.zip -o /tmp/tts-skill.zip && \
mkdir -p ~/.agents/skills/matnoble-tts && \
unzip -qo /tmp/tts-skill.zip -d ~/.agents/skills/matnoble-tts && \
rm /tmp/tts-skill.zip
```

---

## 🎬 核心工作流：配音导演 7 步决策引擎

AI Agent 在接获语音任务时，遵循专业配音导演决策机制：

```text
[1. 审题与体裁识别] ➔ [2. 角色与参数矩阵] ➔ [3. 文本工具预处理] ➔ [4. 导演级语义润色]
                                                                        │
[7. 调用合成与交付]  [6. 质量门禁与自检]      [5. 模式选择与SSML编排] ┘
```

1. **体裁识别与制作蓝图**：自动识别 8 大体裁（双人播客、纪录片、散文诗歌、短视频、教程培训、新闻、有声小说、客服通知）。
2. **音色与黄金参数矩阵**：查阅矩阵配置最优 Voice × Speed × Pitch × Style 组合（如云健纪录片低速深沉、云希短视频轻快网感、晓涵诗歌抒情）。
3. **零依赖工具预处理管道**：
   - **NSW 规范化**：手机/400 电话 (`[say-as:telephone]`)、数字串/工号 (`[say-as:digits]`)、英文缩写 (`[say-as:characters]`)、日期、货币与百分比口语化；
   - **多音字防翻车**：内置 70+ 高频易错词条（重新/重量/行业/说服/西藏等）自动包裹 `[sub:读音]`；
   - **四级韵律启发式注入**：转折词前置呼吸 (`[pause:400ms]`)、设问悬念留白 (`[pause:600ms]`)。
4. **艺术修饰与 SSML 编排**：支持单角色行内指令与多角色交替标准 W3C + 微软 SSML 文档生成。
5. **本地命令行一键合成**：内置零依赖 `scripts/tts_client.py`，直接交付 MP3。

---

## 🛠️ CLI 实用工具速查

```bash
# 1. 纯文本自动预处理（NSW + 多音字防护）
python3 scripts/tts_client.py --preprocess --text "拨打 13800138000 重新核算重量，工号 9527 调用 API"

# 2. 预处理 + 启发式韵律断句注入
python3 scripts/tts_client.py --preprocess --auto-prosody --text "这项技术很强，但是成本很高。你觉得呢？"

# 3. 预览转换为微软标准 SSML
python3 scripts/tts_client.py --to-ssml --text "转折前[pause:400ms]留白。" --voice "zh-CN-YunxiNeural"

# 4. 语法门禁自检（检测指令闭合与参数）
python3 scripts/tts_client.py --validate --text "修饰后文稿..."

# 5. 一键合成出声交付 MP3
python3 scripts/tts_client.py --preprocess --auto-prosody --voice "zh-CN-YunxiNeural" --speed 1.08 --text "大家好！欢迎收听本期科技播客！" -o podcast.mp3

# 6. 多角色 SSML 文件直接合成
python3 scripts/tts_client.py --ssml-file ./duet.xml -o duet.mp3
```

---

## 🔌 开放 REST API 规范 (API Quickstart)

- **官方服务基址**：`https://speak.matnoble.top`
- **鉴权方式**：
  - **公共免 Key 体验通道**：开箱即用（单次 ≤ 500 字，每日公共共享 200 次额度）；
  - **专属 API Key 通道**：请求头携带 `Authorization: Bearer vc_your_key`，单次支持高达 10,000 字长文本自动分块。

### 文字转语音 (TTS)
- **端点**：`POST https://speak.matnoble.top/v1/audio/speech`
- **Content-Type**：`application/json`

#### cURL 调用示例：
```bash
curl -X POST "https://speak.matnoble.top/v1/audio/speech" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "大家好！[pause:300ms]欢迎体验 MatNoble-TTS 配音导演服务！",
    "voice": "zh-CN-YunxiNeural",
    "speed": 1.08,
    "pitch": "+2Hz",
    "style": "chat"
  }' \
  --output speech.mp3
```

---

## 📁 技能知识库结构 (Repository Structure)

```
matnoble-tts-skill/
├── SKILL.md                  # 智能体主控中枢（7步配音导演决策工作流）
├── README.md                 # 项目详细介绍、安装与使用手册
├── package.json              # 技能包元数据
├── references/               # 渐进式下钻专业参考手册
│   ├── scene_profiles.md     # 8 大核心体裁标准化制作蓝图
│   ├── parameter_matrix.md   # Voice × Speed × Pitch × Style 黄金参数矩阵
│   ├── pronunciation_guard.md# 多音字避坑、变调规则与专有名词表
│   ├── prosody_rules.md      # 四级韵律断句与留白规范
│   ├── scriptwriting.md      # 有声文稿艺术修饰实战技巧
│   ├── ssml_templates.md     # 大师级 SSML 模板库（双人播客/诗歌对诵/情绪反转）
│   ├── voices.md             # 26 款神经网络音色定位与决策树
│   ├── directives.md         # 行内语音指令语法速查
│   └── api_reference.md      # REST API 完整规范
└── scripts/
    ├── tts_client.py         # 零依赖预处理管道与合成客户端
    └── test_preprocessor.py  # 预处理器单元测试套件
```

---

## 📄 授权协议 (License)

本项目采用 [MIT License](LICENSE) 许可开源。
服务由 [MatNoble](https://matnoble.top) 维护，欢迎访问主页或提交 Issue 交流！
