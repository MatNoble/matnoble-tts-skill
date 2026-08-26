# 标准 SSML 大师级模板库 (SSML Mastering Templates)

当普通行内指令（Directives）无法满足多角色同台对话、段落间剧烈情绪反转或精细发音控制时，请直接生成**标准 W3C + 微软拓展 SSML 文档**。

MatNoble-TTS 原生支持 SSML 直通模式（通过请求体 `format: "ssml"` 或 CLI `--ssml / --ssml-file` 提交，最大支持 8KB）。

---

## 🏛️ 标准 SSML 语法骨架

所有 SSML 文档必须遵循以下根结构，且必须声明 `xmlns:mstts` 命名空间以支持微软高阶情绪表达：

```xml
<speak version="1.0" 
       xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" 
       xml:lang="zh-CN">
  <!-- 音频内容正文 -->
</speak>
```

> **注意事项（XML 转义）**：
> 正文中的特殊字符必须转义：`&` 转为 `&amp;`，`<` 转为 `&lt;`，`>` 转为 `&gt;`。

---

## 📜 场景一：男女声双人深情朗诵 / 诗歌对诵（舒婷《致橡树》节选）

男声（云健，浑厚沉稳、胸腔共鸣）与女声（晓晓，抒情温婉、坚定细腻）交替出现、同轨合诵，展示了极高水准的艺术感染力与停顿控制：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <!-- 男声：云健 (沉稳浑厚、深情朗诵) -->
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-6%" pitch="-2%">
      我如果爱你——<break time="500ms"/>
      绝不像攀援的凌霄花，借你的高枝炫耀自己；<break time="600ms"/>
      我如果爱你——<break time="500ms"/>
      绝不学痴情的鸟儿，为绿荫重复单调的歌曲。<break time="800ms"/>
    </prosody>
  </voice>

  <!-- 女声：晓晓 (抒情温婉、坚定细腻) -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="lyrical">
      <prosody rate="-4%" pitch="+2%">
        也不止像泉源，常年送来清凉的慰藉；<break time="500ms"/>
        也不止像险峰，增加你的高度，衬托你的威仪。<break time="600ms"/>
        甚至日光，甚至春雨。<break time="700ms"/>
        不，这些都还不够！<break time="500ms"/>
        我必须是你近旁的一株木棉，作为树的形象和你站在一起。<break time="800ms"/>
      </prosody>
    </mstts:express-as>
  </voice>

  <!-- 男声：合诵呼应 -->
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-6%">
      根，紧握在地下；<break time="300ms"/>
      叶，相触在云里。<break time="500ms"/>
      每一阵风过，我们都互相致意。<break time="500ms"/>
    </prosody>
  </voice>

  <!-- 女声：深情收尾 -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="poetry-reading">
      <prosody rate="-8%">
        仿佛永远分离，<break time="400ms"/>
        却又终身相依。
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
```

---

## 🎙️ 场景二：双人播客对白 / 访谈节目

在一个 SSML 文件中，可以通过交替放置 `<voice>` 标签，让男女两位主播在同一音频流中自然交替对话，无需拼接两个独立文件：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <!-- 男声主持人：云希 (轻快聊天风格) -->
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="chat">
      大家好，欢迎收听本期《科技乱弹》。今天我们非常荣幸邀请到了资深 AI 研究员晓晓老师！
      <break time="400ms"/>
      晓晓老师，先和听众朋友们打个招呼吧？<break time="500ms"/>
    </mstts:express-as>
  </voice>

  <!-- 女声嘉宾：晓晓 (温和欢快风格) -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="cheerful" styledegree="1.5">
      嗨，云希好！各位收音机前的朋友们大家好，很高兴今天能来这里做客！<break time="400ms"/>
    </mstts:express-as>
  </voice>

  <!-- 主持人抛出核心话题 -->
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="chat">
      听说你们团队最近开源了一款全栈语音平台，主打极速响应和边缘流控，能跟我们具体聊聊吗？
    </mstts:express-as>
  </voice>
</speak>
```

---

## 🎭 场景二：剧情叙事与情绪动态反转

同一个说话者在讲故事时，情绪往往随着情节跌宕起伏。通过嵌套不同 `style`，可实现情绪的平滑切换：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-YunyangNeural">
    <!-- 阶段 1: 轻松日常 -->
    <mstts:express-as style="cheerful">
      那天清晨，阳光刚刚透过窗帘洒在桌面上，一切都显得无比惬意。
    </mstts:express-as>

    <break time="600ms"/>

    <!-- 阶段 2: 突发危机（转为严肃紧张与放慢语速） -->
    <mstts:express-as style="serious" styledegree="2.0">
      <prosody rate="-10%" pitch="-5%">
        直到突然，尖锐的警报声划破了长空。<break time="400ms"/>
        雷达屏幕上，一个未知信号正在以惊人的速度极速逼近！
      </prosody>
    </mstts:express-as>

    <break time="800ms"/>

    <!-- 阶段 3: 屏息沉思（极慢与低沉） -->
    <mstts:express-as style="calm">
      <prosody rate="-15%" pitch="-10%">
        所有人都屏住了呼吸，没有人知道，这一秒究竟意味着终结，还是新生。
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
```

---

## 🏛️ 场景三：纪录片 / 严肃科普深度旁白

采用 `zh-CN-YunjianNeural`（云健，厚重男声）配合音调微调，呈现央视《舌尖上的中国》或地理纪录片质感：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-8%" pitch="-5%">
      时间，是一切奥秘的注脚。<break time="600ms"/>
      在青藏高原高耸入云的崇山峻岭之中，冰川经历了数万年的沉睡与消融。
      <break time="500ms"/>
      当第一缕季风拂过山脊，生命的故事，便在这片荒原上悄然生根。
    </prosody>
  </voice>
</speak>
```

---

## 🌐 场景四：中英双语混排与专业术语发音规范

在技术与商业播报中，英文缩写如果直接读可能会被引擎当成词汇拼读。通过 `<say-as>` 和 `<sub>` 规范发音：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="zh-CN-XiaochenNeural">
    本次技术架构升级，全面整合了
    <!-- 强制逐字母朗读字母缩写 -->
    <say-as interpret-as="characters">API</say-as>
    网关与边缘
    <say-as interpret-as="characters">TTS</say-as>
    节点。<break time="300ms"/>
    通过引入
    <!-- 专有名词读音别名映射 -->
    <sub alias="Kubernetes">K8s</sub>
    集群，单节点的
    <say-as interpret-as="characters">QPS</say-as>
    提升了整整三倍！
  </voice>
</speak>
```

---

## 📱 场景五：智能客服通知与账单提醒

规范电话、日期、金额、卡号朗读：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="customerservice">
      尊敬的贵宾客户，您好！<break time="300ms"/>
      您尾号为 <say-as interpret-as="digits">8899</say-as> 的账户，
      于 <say-as interpret-as="date">2026-08-26</say-as> 成功扣款人民币 
      <emphasis level="moderate">128.50</emphasis> 元。
      <break time="400ms"/>
      若非本人操作，请立即致电客服专线：
      <say-as interpret-as="telephone">4008109999</say-as> 办理挂失。
    </mstts:express-as>
  </voice>
</speak>
```

---

## 🛠️ 如何使用 CLI 执行 SSML

Agent 在生成上述 SSML 后，可直接通过内置工具一步出声：
```bash
# 方式 1：直接通过字符串参数执行
python3 skill/scripts/tts_client.py --ssml '<speak version="1.0" ...>...</speak>' --output result.mp3

# 方式 2：将 SSML 保存为文件后执行 (推荐，避免命令行过长)
python3 skill/scripts/tts_client.py --ssml-file podcast.xml --output podcast.mp3
```
