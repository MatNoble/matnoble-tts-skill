# 分体裁场景制作手册 (Scene Profiles & Production Blueprints)

本手册为 AI 配音导演提供 **8 大核心文稿体裁** 的标准化制作蓝图。当收到用户的文稿时，请首先识别其所属体裁，并严格参照对应的角色配置、情绪曲线、节奏编排与 SSML 骨架进行制作。

---

## 🎙️ 1. 双人播客与访谈 (Two-Host Podcast & Interview)

### 适用场景
科技杂谈、行业访谈、文化对谈、观点交锋。

### 角色配置黄金模板
- **主咖 / 主持人**：`zh-CN-YunxiNeural`（云希·男） | `style="chat"` | `speed=1.05` | `pitch=0`
- **副咖 / 嘉宾**：`zh-CN-XiaoxiaoNeural`（晓晓·女） | `style="cheerful"` `styledegree="1.3"` | `speed=1.0` | `pitch=+2`
- *设计意图*：一男一女声线频段分离度极高，听众无需画面即可瞬间区分发言人。

### 节奏与呼吸编排规则
- **对白轮替间隔**：每段说话人间切换时，强制插入 `[pause:400ms]`（快节奏接话）至 `[pause:600ms]`（话题转换）。
- **自然语气词处理**：保留“哈哈”、“确实”、“对”、“嗯”等语气词，切忌删成公文体。
- **开场与收尾**：开场背景铺垫 `[pause:500ms]`，结尾总结留白 `[pause:800ms]`。

### 情绪曲线
```
[开场破冰: 轻松幽默 cheerful] ➔ [核心探讨: 专注自然 chat] ➔ [观点交锋: 严肃强调 serious] ➔ [总结致谢: 温和愉悦 cheerful]
```

### 标准 SSML 编排模板
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <!-- 主持人开场 -->
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="chat">
      大家好，欢迎收听本期播客！[pause:300ms]今天我们请到了老朋友晓晓，一起聊聊最近大火的 AI 语音技术。<break time="500ms"/>晓晓，先和大家打个招呼吧？
    </mstts:express-as>
  </voice>

  <!-- 嘉宾回应 -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="cheerful" styledegree="1.3">
      嗨云希，收音机前的朋友们大家好！<break time="300ms"/>非常开心又来做客啦！
    </mstts:express-as>
  </voice>
</speak>
```

---

## 👥 2. 多人播客与圆桌讨论 (Multi-Speaker Panel)

### 适用场景
3 人及以上圆桌漫谈、剧本对白、辩论赛。

### 角色配置原则
- **声线反差最大化**：
  - 角色 A（主持人/控场）：`zh-CN-YunxiNeural`（青年阳光男声）
  - 角色 B（专业专家）：`zh-CN-YunjianNeural`（沉稳厚重男声）
  - 角色 C（行业代表）：`zh-CN-XiaochenNeural`（知性从容女声）
- **发言标识规范**：在 SSML 中为每位发言者包裹独立的 `<voice>` 标签，角色切换前必须注入 `<break time="500ms"/>`。

---

## 📖 3. 有声电子书与故事叙述 (Audiobook & Fiction)

### 适用场景
小说演播、故事绘本、睡前读物、人物传记。

### 角色配置黄金模板
- **旁白叙述者**：`zh-CN-YunjianNeural`（云健，男）或 `zh-CN-XiaohanNeural`（晓涵，女）
- **推荐参数**：`speed=0.95` | `pitch=-3` | `style="calm"`
- *设计意图*：语速略微放慢，降低音调，营造深度故事沉浸感与厚重感。

### 节奏编排规则
- **章节切换**：`[pause:1.5s]`
- **段落与场景切换**：`[pause:800ms]`
- **对话前后**：角色开口前 `[pause:400ms]`，语毕后 `[pause:500ms]`。

---

## 🎭 4. 现代诗歌与散文朗诵 (Poetry & Prose)

### 适用场景
现代诗歌、抒情散文、情书诵读、纪念致辞。

### 角色配置黄金模板
- **男声合诵**：`zh-CN-YunjianNeural` | `style="lyrical"` | `speed=0.88` | `pitch=-2`
- **女声合诵**：`zh-CN-XiaohanNeural` / `zh-CN-XiaoxiaoNeural` | `style="lyrical"` | `speed=0.90` | `pitch=+2`

### 节奏编排规则
- **字句留白密度极高**：每行诗句末尾插入 `[pause:600ms]` 到 `[pause:1s]`。
- **意象词强调**：对诗眼、核心意象使用 `[emphasis:moderate]`，切忌使用生硬的 `strong`。

---

## 📢 5. 权威新闻与公文播报 (News & Official Broadcast)

### 适用场景
新闻简报、政府公文、企业财报、发布会公报。

### 角色配置黄金模板
- **播音主播**：`zh-CN-YunyangNeural`（云扬·男，播音腔）或 `zh-CN-XiaochenNeural`（晓辰·女，干练精英）
- **推荐参数**：`speed=1.0` | `pitch=0` | `style="general"`

### 编排规则
- **标题后停顿**：`[pause:500ms]`
- **数据与专有名词**：数字严格采用 `[say-as:digits]` 或自然展开，年份采用 `[say-as:date]`，英文缩写采用 `[say-as:characters]`。
- **语气特点**：客观、平稳、字正腔圆，不宜有剧烈的情绪起伏。

---

## 🎓 6. 课程培训与知识讲解 (Tutorial & Courseware)

### 适用场景
在线课程、技术评测、操作教程、产品功能说明。

### 角色配置黄金模板
- **讲师**：`zh-CN-XiaochenNeural`（晓辰）或 `zh-CN-YunxiNeural`（云希）
- **推荐参数**：`speed=1.02` | `pitch=0` | `style="assistant"`

### 节奏编排规则
- **核心概念提出前**：减速 `[rate:slow]` 并加重 `[emphasis:strong]`。
- **代码与参数枚举**：逐项停顿 `[pause:300ms]`，英文术语规范逐字母或标准发音。

---

## ⚡ 7. 短视频抓耳文案 (Short Video & Vlog)

### 适用场景
抖音/快手/B站短视频旁白、带货解说、Vlog 剪辑配音。

### 角色配置黄金模板
- **解说员**：`zh-CN-YunxiNeural`（云希） | `style="chat"` | `speed=1.1` | `pitch=+2`
- **甜美带货**：`zh-CN-XiaoyiNeural`（晓伊） | `style="cheerful"` | `speed=1.08` | `pitch=+4`

### 节奏编排规则
- **快节奏、高密度**：句间停顿短（`[pause:200ms~300ms]`），拒绝冷场。
- **黄金 3 秒 Hook**：开篇第一句话必须使用 `[emphasis:strong]` 锁定听众注意力。

---

## ☎️ 8. 客服坐席与系统通知 (IVR & Notification)

### 适用场景
400 电话导航、账单变动提醒、取件码通知、App 提示音。

### 角色配置黄金模板
- **客服代表**：`zh-CN-XiaoxiaoNeural` | `style="customerservice"` | `speed=1.0` | `pitch=0`

### 编排规则
- **必须执行预处理**：电话号码强制 `[say-as:telephone]`，验证码/取件码强制 `[say-as:digits]`，金额强制规范口语化。
- **句末留白**：重要操作指令后留白 `[pause:500ms]` 方便听众记录。
