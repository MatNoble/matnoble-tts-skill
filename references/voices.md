# 音色全谱与场景推荐指南 (Voice Persona & Selection Matrix)

MatNoble-TTS 搭载了微软 Edge 全套超拟真神经网络音色（Neural Voices）。
为了让合成的音频更具感染力，**请根据文案内容属性，为角色挑选最贴合的人设与音色**。

---

## 🌟 常用中文音色矩阵

| 音色 ID (`voice`) | 角色名称 | 性别 | 声线特点 | 黄金适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| `zh-CN-XiaoxiaoNeural` | **晓晓**（默认） | 女 | 亲切自然、温婉明澈、全能通用 | 智能助手、日常生活、教程解说、客服 |
| `zh-CN-YunxiNeural` | **云希** | 男 | 阳光清朗、极具网感、节奏明快 | 科技解说、短视频配音、播客对白、Vlog |
| `zh-CN-YunyangNeural` | **云扬** | 男 | 专业端庄、字正腔圆、播音级气场 | 官方新闻播报、发布会演讲、企业形象片 |
| `zh-CN-YunjianNeural` | **云健** | 男 | 浑厚稳重、胸腔共鸣、故事感强 | 央视级纪录片、历史长卷、深度有声书 |
| `zh-CN-XiaoyiNeural` | **晓伊** | 女 | 甜美灵动、轻快活泼、略带童趣 | 儿童绘本、休闲聊天、动漫二次元、萌系配音 |
| `zh-CN-XiaochenNeural` | **晓辰** | 女 | 知性内敛、从容干练、职场精英 | 财经资讯、科技评测、商业报告、职场课程 |
| `zh-CN-XiaohanNeural` | **晓涵** | 女 | 抒情细腻、优雅恬静、情绪层次丰富 | 文学散文、现代诗歌、情感电台、走心独白 |
| `zh-CN-YunfengNeural` | **云枫** | 男 | 磁性低沉、略带沙哑、悬念感十足 | 悬疑推理、深夜情感热线、科幻奇幻有声书 |
| `zh-CN-XiaomengNeural` | **晓梦** | 女 | 轻柔梦幻、舒缓放松 | 睡前故事、冥想引导、助眠播客 |
| `zh-CN-XiaoruiNeural` | **晓睿** | 女 | 成熟睿智、逻辑清晰 | 深度讲书、知识付费专栏、学术分享 |

---

## 🌏 方言与跨语言精选音色

| 音色 ID (`voice`) | 语言/方言 | 性别 | 适用场景 |
| :--- | :--- | :--- | :--- |
| `zh-HK-HiuMaanNeural` | 粤语（香港） | 女 | 粤港澳大湾区资讯、粤语播客、港剧配音 |
| `zh-HK-WanLungNeural` | 粤语（香港） | 男 | 粤语商业播报、纪录片 |
| `zh-TW-HsiaoChenNeural`| 台湾国语 | 女 | 台湾腔自然会话、小清新短视频 |
| `en-US-JennyNeural` | 英语（美式） | 女 | 英文科技解说、英语教学、商务演讲 |
| `en-US-GuyNeural` | 英语（美式） | 男 | 英文故事叙述、播客主持 |
| `ja-JP-NanamiNeural` | 日语 | 女 | 日语动漫对白、产品说明 |
| `ko-KR-SunHiNeural` | 韩语 | 女 | 韩流文化、日常会话 |

---

## 🎯 业务场景快速决策树

在不知道选什么声音时，可直接参考以下搭配：

1. **科技 / 软件评测 / B 站 YouTube 短视频**：
   - 首选：`zh-CN-YunxiNeural` (云希)
   - 理由：节奏感强、发音自然亲近、符合当代互联网短视频听觉习惯。
2. **播客双人对谈 (Podcast)**：
   - 主持人：`zh-CN-YunxiNeural` (云希，男)
   - 嘉宾：`zh-CN-XiaoxiaoNeural` (晓晓，女)
   - 理由：一男一女声线辨识度极高，听众无需看画面就能清晰分辨说话人。
3. **纪录片 / 严肃科普 / 历史回眸**：
   - 首选：`zh-CN-YunjianNeural` (云健)
   - 配合参数：`speed=0.95`, `pitch="-5"`
   - 理由：气场厚重沉稳，极具央视质感。
4. **企业客服电话 / 微信服务号语音播报**：
   - 首选：`zh-CN-XiaoxiaoNeural` (晓晓) 或 `zh-CN-XiaochenNeural` (晓辰)
   - 风格：`style="customerservice"`
5. **儿童童话 / 轻松绘本**：
   - 首选：`zh-CN-XiaoyiNeural` (晓伊)
   - 风格：`style="cheerful"`
