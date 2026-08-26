---
name: matnoble-tts
description: AI 语音合成（TTS）、配音创作、播客对白制作与语音转文字（STT）专业工具。当用户想要将文本转为语音、生成朗读配音、制作有声书、创作双人播客、测试语音指令、修饰配音节奏（添加停顿/重音/语速起伏）、生成标准 SSML 文稿，或将音频转为文本时，必须使用本技能。支持免配置开箱即用（默认连接官方公共体验通道 https://speak.matnoble.top）或挂载专属 API Key。
---

# MatNoble-TTS：配音导演与语音创作技能

本技能赋予你**“专业配音导演（Audio Director）”**的能力。你不仅能调用接口将文字转化为高质量 MP3，更能主动优化文稿的有声表达——通过添加呼吸停顿、重音起伏与发音修正，甚至编排多角色标准 SSML 文稿。

---

## 🚀 核心工作流 (The 4-Step Audio Production Workflow)

当收到用户的语音合成任务时，请遵循以下四步专业流程：

```text
[1. 审听与导演润色] ➔ [2. 人设与音色匹配] ➔ [3. 语法自检/SSML编排] ➔ [4. 调用生成与交付]
```

### 第一步：审听与导演润色 (Audio Script Directing)
**拒绝机械朗读！** 书面文字直接转语音往往平淡、冰冷且缺乏呼吸感。请参考 [`references/scriptwriting.md`](./references/scriptwriting.md) 对文稿进行修饰：
1. **呼吸留白**：在设问后、段落转折前（如“但是”、“然而”）插入 `[pause:300ms]` 到 `[pause:600ms]`。
2. **重点突出**：在核心论点、品牌词或行动号召处包裹 `[emphasis:strong]关键词[/emphasis]`。
3. **节奏张弛**：重要数据放慢 `[rate:slow]`，轻松过渡可加快 `[rate:fast]`。
4. **读音防踩坑**：
   - 手机/电话号码强制包裹：`[say-as:telephone]13800138000[/say-as]`（避免“幺”读成“一”）。
   - 纯数字/流水号强制包裹：`[say-as:digits]9527[/say-as]`（避免读成“九千五百二十七”）。
   - 英文缩写强制逐字母读：`[say-as:characters]API[/say-as]`。

### 第二步：人设与音色匹配 (Voice Selection)
根据文稿题材，查阅 [`references/voices.md`](./references/voices.md) 挑选最契合的声音角色：
- **短视频/科技解说/现代网感**：`zh-CN-YunxiNeural`（云希，男）
- **官方新闻/发布会演讲/权威播报**：`zh-CN-YunyangNeural`（云扬，男）
- **纪录片/深度历史/央视气场**：`zh-CN-YunjianNeural`（云健，男）
- **智能助手/温馨日常/客服说明**：`zh-CN-XiaoxiaoNeural`（晓晓，女，默认）
- **文学散文/走心诗歌/情感电台**：`zh-CN-XiaohanNeural`（晓涵，女）
- **少儿故事/轻松绘本/二次元**：`zh-CN-XiaoyiNeural`（晓伊，女）

### 第三步：模式选择（行内指令 vs 标准 SSML）
根据任务复杂度选择最佳表达载体：
- **方案 A：行内指令模式（单角色快捷配音，最常用）**
  - 在普通文本中直接嵌入 `[pause]`, `[emphasis]`, `[rate]`, `[say-as]` 即可。
  - 语法速查详见 [`references/directives.md`](./references/directives.md)。
- **方案 B：标准 SSML 大师模式（双人播客/多情绪对白）**
  - 当需要两个角色同台交替对谈（如男主播云希 + 女嘉宾晓晓），或需要同一角色切换 `cheerful` / `serious` 情绪时，编写完整 SSML 文档。
  - 模板库详见 [`references/ssml_templates.md`](./references/ssml_templates.md)。

### 第四步：调用合成与交付 (Execution & Delivery)
**优先使用内置的零依赖 Python 工具**，可避免在命令行拼接 cURL 时极易遇到的单双引号转义、多行字符丢失和换行符报错问题。

---

## 🛠️ 执行方式：推荐使用内置 CLI 工具

脚本路径：[`scripts/tts_client.py`](./scripts/tts_client.py)（纯 Python 标准库编写，无需 `pip install` 任何依赖）。

### 1. 基础文本合成（自动使用官方公共体验通道）
```bash
python3 skill/scripts/tts_client.py \
  --text "大家好！[pause:400ms][emphasis:strong]欢迎体验全新配音服务[/emphasis]。" \
  --output speech.mp3
```

### 2. 指定音色、语速与风格
```bash
python3 skill/scripts/tts_client.py \
  --voice "zh-CN-YunxiNeural" \
  --speed 1.05 \
  --style "chat" \
  --text "今天的科技速报，[pause:300ms]我们先来看第一条动态。" \
  --output tech_news.mp3
```

### 3. 长文本读取（从文件读取）
```bash
python3 skill/scripts/tts_client.py \
  --file ./article.txt \
  --voice "zh-CN-YunjianNeural" \
  --output narration.mp3
```

### 4. 标准 SSML 文件直接合成（播客 / 多角色对白）
```bash
python3 skill/scripts/tts_client.py \
  --ssml-file ./podcast.xml \
  --output podcast.mp3
```

### 5. 辅助自检与转换（免网络发包）
```bash
# 验证指令语法是否全部闭合
python3 skill/scripts/tts_client.py --validate --text "测试文本[emphasis:strong]语法检查[/emphasis]"

# 本地将指令预览转换为标准 SSML
python3 skill/scripts/tts_client.py --to-ssml --text "转折前[pause:500ms]留白。"
```

### 6. 查询配额用量
```bash
python3 skill/scripts/tts_client.py --check-usage
```

---

## 🌐 替代方案：原生 cURL 调用

若宿主环境未安装 Python，可直接通过 `curl` 交互：

```bash
curl -X POST "https://speak.matnoble.top/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "大家好[pause:500ms][emphasis:strong]欢迎体验[/emphasis]智能配音服务。",
    "voice": "zh-CN-XiaoxiaoNeural",
    "speed": 1.0
  }' \
  --output output.mp3
```

*若有专属 API Key，加入请求头：`-H "Authorization: Bearer vc_your_key"`。*

---

## ⚠️ 配额、分段与限制管理

1. **公共体验通道（免 Key）**：
   - 默认服务地址：`https://speak.matnoble.top`。
   - **单次文本上限 500 字**（SSML 上限 2KB），每日全局共享 200 次。
   - **长文本分段策略**：如果用户提供的文本超过 500 字，请主动在逻辑段落（句号/换行）处将文本拆分为 `<= 450 字` 的若干小节，分批合成出多个音频文件（如 `part1.mp3`, `part2.mp3`），或提示用户在个人主页获取专属 Key。
2. **专属 API Key 通道**：
   - 支持更高单次字符上限（高达 10,000 字）与独立高配额。
   - 可通过环境变量指定：
     ```bash
     export MATNOBLE_TTS_ENDPOINT="https://speak.matnoble.top"
     export MATNOBLE_TTS_API_KEY="vc_your_key"
     ```

---

## 📚 延伸参考文档索引

- [有声文稿导演与润色指南 (`references/scriptwriting.md`)](./references/scriptwriting.md)
- [标准 SSML 大师级模板库 (`references/ssml_templates.md`)](./references/ssml_templates.md)
- [行内语音指令速查手册 (`references/directives.md`)](./references/directives.md)
- [音色全谱与场景推荐 (`references/voices.md`)](./references/voices.md)
- [OpenAI 兼容 REST API 规范 (`references/api_reference.md`)](./references/api_reference.md)
