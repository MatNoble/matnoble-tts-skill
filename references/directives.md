# 行内语音指令速查手册 (Inline Voice Directives)

在 MatNoble-TTS 中，普通文本模式原生支持轻量级的**行内指令（Inline Directives）**。
您无需编写复杂的 XML/SSML，只需在文本中像写 Markdown 标签一样嵌入 `[...]` 标记，服务端会自动在毫秒内将其精准解析为对应的微软 Neural 语音控制流。

---

## ⚡ 核心指令速查表

| 指令语法 | 闭合标签 | 典型参数取值 | 对应 SSML 效果 | 范例 |
| :--- | :--- | :--- | :--- | :--- |
| `[pause:时间]` | *单标签* | `300ms`, `500ms`, `1s`, `2s` | `<break time="..."/>` | `请稍候[pause:500ms]正在加载` |
| `[emphasis:等级]` | `[/emphasis]` | `strong` (强), `moderate` (中), `reduced` (弱) | `<emphasis level="..."/>` | `这是[emphasis:strong]重中之重[/emphasis]` |
| `[rate:速度]` | `[/rate]` | `slow`, `fast`, `+20%`, `-10%` | `<prosody rate="..."/>` | `请听好：[rate:slow]关键密码[/rate]` |
| `[pitch:音调]` | `[/pitch]` | `high`, `low`, `+15%`, `-10%`, `+20Hz` | `<prosody pitch="..."/>` | `[pitch:high]真的吗？[/pitch]` |
| `[volume:音量]` | `[/volume]` | `loud`, `soft`, `+6dB`, `-3dB` | `<prosody volume="..."/>` | `[volume:loud]注意安全！[/volume]` |
| `[say-as:类型]` | `[/say-as]` | `telephone`, `digits`, `date`, `characters` | `<say-as interpret-as="..."/>` | `电话：[say-as:telephone]13800138000[/say-as]` |
| `[sub:读音]` | `[/sub]` | 替换的文字或拼音 | `<sub alias="..."/>` | `[sub:beijing]BJ[/sub]` |
| `[style:风格:强度]` | `[/style]` | 风格名，强度 0.1~2.0 (如 `cheerful:1.5`) | `<mstts:express-as style="..."/>` | `[style:cheerful:1.5]太棒了！[/style]` |

---

## 🔍 指令参数详解与约束

### 1. `[pause]` (停顿 / 留白)
- **参数格式**：
  - 毫秒格式：`[pause:300ms]`、`[pause:800ms]`
  - 秒格式：`[pause:1s]`、`[pause:1.5s]`
  - 预设语义：`[pause:weak]` (200ms)、`[pause:medium]` (400ms)、`[pause:strong]` (800ms)
- **安全约束**：
  - 单次停顿最长为 **5000ms (5秒)**。
  - 全文累计停顿时间建议控制在 30 秒以内。
  - 无参数默认：`[pause]` 等同于 `[pause:medium]` (400ms)。

### 2. `[emphasis]` (重音与强调)
- **可用等级**：
  - `strong`：强强调，音量略升、发音加重（最常用）。
  - `moderate`：适中强调。
  - `reduced`：弱化朗读。
- **范例**：`请务必在[emphasis:strong]今日下班前[/emphasis]完成审批。`

### 3. `[say-as]` (发音解释器)
极为关键，专门解决中文数字与特殊字符读错：
- `[say-as:telephone]...[/say-as]`：按电话号码逐位读出，并自动将“1”转为“幺”。
- `[say-as:digits]...[/say-as]`：按纯数字串逐位念出（如工号 `9527` 读作“九五二七”，而非“九千五百二十七”）。
- `[say-as:characters]...[/say-as]`：英文字母逐个拼读（如 `[say-as:characters]NASA[/say-as]` 读作“N-A-S-A”）。
- `[say-as:date]...[/say-as]`：按规范日期朗读（如 `2026-08-26` 读作“二零二六年八月二十六日”）。

### 4. `[style]` (局部情绪切换)
在同一个音色中局部调整说话情感：
- **语法**：`[style:风格名:强度数值]`
- **常用风格名**：`cheerful` (高兴), `serious` (严肃), `calm` (平静), `assistant` (助手), `chat` (闲聊), `customerservice` (客服)。
- **强度 (Style Degree)**：范围为 `0.1` ~ `2.0`（默认约为 1.0~1.5）。
- **范例**：`[style:serious:1.8]这是一场没有退路的战役。[/style]`

---

## 🛠️ 本地校验与 SSML 预览

在正式请求前，建议 Agent 使用内置的 `tts_client.py` 进行静态校验：

```bash
# 1. 验证标签闭合性与参数范围
python3 skill/scripts/tts_client.py --validate --text "文本内容..."

# 2. 本地转换为标准 SSML 预览查看
python3 skill/scripts/tts_client.py --to-ssml --text "转折前[pause:500ms]稍作停顿。"
```
