---
name: matnoble-tts
description: AI 语音合成（TTS）、配音创作、播客对白制作、多音字与发音防护、语音指令编排专业工具。当用户想要将文本转为语音、生成朗读配音、制作有声书、创作双人/多人播客、测试语音指令、修饰配音节奏（添加呼吸停顿/重音/语速起伏/多音字校音）、生成标准 SSML 文稿时，必须使用本技能。支持免配置开箱即用（默认连接官方公共体验通道 https://speak.matnoble.top）或挂载专属 API Key。
---

# MatNoble-TTS：专业 AI 配音导演与语音创作技能 (Director 2.0)

本技能赋予你**“专业配音导演（Audio Director）”**的全套能力。你不仅能调用接口将文字转化为超高音质 MP3，更能基于文稿体裁自主执行**体裁识别、黄金音色参数匹配、非标准词与多音字防护、四级韵律留白、多角色 SSML 编排与质量门禁**。

---

## 🎬 核心工作流：配音导演 7 步决策引擎

当收到用户的语音合成任务时，请严格遵循以下 7 步专业配音导演工作流：

```text
[1. 审题与体裁识别] ➔ [2. 角色规划与音色矩阵] ➔ [3. 文本工具预处理] ➔ [4. 导演级语义润色]
                                                                        │
[7. 调用合成与交付]  [6. 质量门禁与自检]      [5. 模式选择与SSML编排] ┘
```

---

### 第一步：文稿审题与体裁识别 (Scene Identification)
**拒绝千篇一律！** 分析输入文稿的语义、题材与形式，识别其所属场景体裁，并查阅 [`references/scene_profiles.md`](./references/scene_profiles.md) 加载对应蓝图：
- **双人/多人播客**：查阅播客蓝图，准备多角色 SSML 交替对白。
- **纪录片/深度叙事**：加载云健央视级质感方案（低语速、深沉音调、大留白）。
- **现代诗歌/散文**：加载晓涵/晓晓抒情方案（高停顿密度、韵味沉淀）。
- **短视频/科技解说**：加载云希网感方案（高语速、短停顿、抓耳 Hook）。
- **课程讲解/客服通知**：加载晓辰/晓晓清晰规范方案。

### 第二步：角色规划与音色参数匹配 (Voice & Parameter Matrix)
根据体裁人设需求，查阅 [`references/parameter_matrix.md`](./parameter_matrix.md) 选取最匹配的 **Voice × Speed × Pitch × Style** 黄金组合，并生成“制作参数卡”：
- **云健（男·浑厚）**：纪录片 `speed=0.92, pitch=-5Hz, style="calm"`
- **云希（男·清朗）**：短视频 `speed=1.08, pitch=+2Hz, style="chat"`
- **晓晓（女·温婉）**：播客嘉宾 `speed=1.00, pitch=+2Hz, style="cheerful:1.3"`
- **晓涵（女·抒情）**：诗歌电台 `speed=0.90, pitch=+2Hz, style="lyrical"`

### 第三步：文本工具预处理 (Tool Preprocessing)
调用内置 CLI 脚本执行非标准词规范化（NSW）与高频多音字防护：
```bash
python3 skill/scripts/tts_client.py --preprocess --text "原始文稿..."
```
- **自动拦截 NSW**：手机/400 电话 $\rightarrow$ `[say-as:telephone]`、纯数字串/验证码 $\rightarrow$ `[say-as:digits]`、英文缩写 $\rightarrow$ `[say-as:characters]`、货币/百分比自动口语化。
- **自动拦截多音字**：重新/重量/行业/说服/西藏等 70+ 词条自动包裹 `[sub:读音]`。

### 第四步：导演级语义润色 (Director Creative Scripting)
在工具预处理生成的文本基础上，参考 [`references/scriptwriting.md`](./references/scriptwriting.md) 与 [`references/prosody_rules.md`](./references/prosody_rules.md) 进行艺术润色：
1. **四级韵律与呼吸留白**：
   - 逻辑转折词（但是/然而/更重要的是）前置呼吸：`[pause:400ms]`
   - 设问句后悬念留白：`[pause:600ms]`
   - 章节与段落沉淀：`[pause:800ms ~ 1s]`
2. **重点与重音强调**：在核心论点或品牌词处添加 `[emphasis:strong]`。
3. **情绪动态起伏**：根据剧情反转局部添加 `[style:serious]` 或 `[style:cheerful]`。

### 第五步：模式选择与 SSML 编排 (SSML Mastering)
根据体裁复杂度选择生成载体：
- **方案 A：单角色行内指令模式（最常用）**：直接使用修饰后的文本及 `[...]` 指令。
- **方案 B：标准 SSML 模式（双人播客 / 多角色对白）**：参考 [`references/ssml_templates.md`](./references/ssml_templates.md) 编排包含交替 `<voice>` 的标准 W3C SSML 文档。

### 第六步：质量门禁与安全自检 (Quality Gate)
在正式请求前，执行静态自检：
```bash
# 校验指令闭合性与参数合法性
python3 skill/scripts/tts_client.py --validate --text "修饰后文稿..."
```
- 检查 [`references/pronunciation_guard.md`](./references/pronunciation_guard.md) 中的生僻专有名词是否已有注音保护。
- 确认全文总停顿不超过 30 秒、单次停顿不超过 5000ms。

### 第七步：调用合成与交付 (Execution & Delivery)
优先使用内置的零依赖 Python 工具完成音频交付：
```bash
# 单角色指令合成
python3 skill/scripts/tts_client.py \
  --voice "zh-CN-YunxiNeural" \
  --speed 1.08 \
  --style "chat" \
  --text "大家好！[pause:300ms][emphasis:strong]欢迎体验全新配音服务[/emphasis]。" \
  --output speech.mp3

# 多角色 SSML 合成
python3 skill/scripts/tts_client.py \
  --ssml-file ./podcast.xml \
  --output podcast.mp3
```

---

## 🛠️ CLI 实用指令速查

| 操作场景 | 命令行示例 |
| :--- | :--- |
| **纯文本自动预处理** | `python3 skill/scripts/tts_client.py --preprocess --text "拨打 13800138000 重新核算重量。"` |
| **预处理 + 韵律断句** | `python3 skill/scripts/tts_client.py --preprocess --auto-prosody --text "文本..."` |
| **一键合成出声** | `python3 skill/scripts/tts_client.py --preprocess --voice "zh-CN-YunjianNeural" --speed 0.92 --text "..." -o doc.mp3` |
| **SSML 本地预览** | `python3 skill/scripts/tts_client.py --to-ssml --text "转折前[pause:500ms]留白。"` |
| **语法门禁自检** | `python3 skill/scripts/tts_client.py --validate --text "..."` |
| **查询配额用量** | `python3 skill/scripts/tts_client.py --check-usage` |

---

## ⚠️ 配额、分段与限制管理

1. **公共体验通道（免 Key）**：
   - 默认服务基址：`https://speak.matnoble.top`（单次 $\le 500$ 字，每日 200 次）。
   - **长文本分段策略**：若用户文本超过 500 字，请主动在段落换行或句号处拆分为 $\le 450$ 字的小节分别合成（如 `part1.mp3`, `part2.mp3`）。
2. **专属 API Key 通道**：
   - 支持单次高达 10,000 字与独立配额。可通过环境变量配置：
     ```bash
     export MATNOBLE_TTS_ENDPOINT="https://speak.matnoble.top"
     export MATNOBLE_TTS_API_KEY="vc_your_key"
     ```

---

## 📚 延伸参考文档索引 (References)

- [8 大文稿体裁标准化制作手册 (`references/scene_profiles.md`)](./references/scene_profiles.md)
- [Voice × Speed × Pitch × Style 黄金参数矩阵 (`references/parameter_matrix.md`)](./references/parameter_matrix.md)
- [高频多音字与发音防翻车指南 (`references/pronunciation_guard.md`)](./references/pronunciation_guard.md)
- [四级韵律断句与停顿指南 (`references/prosody_rules.md`)](./references/prosody_rules.md)
- [有声文稿配音导演实战教程 (`references/scriptwriting.md`)](./references/scriptwriting.md)
- [标准 SSML 大师级模板库 (`references/ssml_templates.md`)](./references/ssml_templates.md)
- [音色全谱与场景决策矩阵 (`references/voices.md`)](./references/voices.md)
- [行内语音指令语法速查 (`references/directives.md`)](./references/directives.md)
- [OpenAI 兼容 REST API 规范 (`references/api_reference.md`)](./references/api_reference.md)
