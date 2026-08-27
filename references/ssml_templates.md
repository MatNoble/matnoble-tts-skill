# 标准 SSML 大师级模板库 (SSML Mastering Templates)

当普通单角色行内指令（Directives）无法满足多角色同台对话、段落间剧烈情绪反转或极精细控制时，请直接生成**标准 W3C + 微软拓展 SSML 文档**。

MatNoble-TTS 原生支持 SSML 直通模式（通过请求体 `format: "ssml"` 或 CLI `--ssml / --ssml-file` 提交，最大支持 8KB）。

---

## 🏛️ 标准 SSML 语法规范骨架

所有 SSML 文档必须遵循以下根结构，且必须声明 `xmlns:mstts` 命名空间：

```xml
<speak version="1.0" 
       xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" 
       xml:lang="zh-CN">
  <!-- 音频内容正文 -->
</speak>
```

> **XML 字符转义规则**：
> 正文中的特殊字符必须转义：`&` $\rightarrow$ `&amp;`，`<` $\rightarrow$ `&lt;`，`>` $\rightarrow$ `&gt;`。

---

## 🎙️ 模板一：双人播客 / 访谈对白 (Two-Host Podcast)

男声主持人（云希·轻快聊天）与女声嘉宾（晓晓·温和欢快）在同一音频流中自然交替：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <!-- 男声主持人：云希 -->
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="chat">
      大家好，欢迎收听《科技杂谈》！<break time="300ms"/>
      今天我们邀请到了 AI 语音领域的资深工程师晓晓老师！
      <break time="500ms"/>
      晓晓老师，先和听众朋友们打个招呼吧？
    </mstts:express-as>
  </voice>

  <!-- 对白切换停顿 -->
  <break time="400ms"/>

  <!-- 女声嘉宾：晓晓 -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="cheerful" styledegree="1.3">
      嗨云希好，收音机前的各位朋友们大家好！<break time="300ms"/>
      非常高兴今天能在这里和大家交流！
    </mstts:express-as>
  </voice>

  <break time="400ms"/>

  <!-- 主持人抛出核心议题 -->
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="chat">
      听说你们最近上线了全新的边缘流控语音中枢，能跟我们聊聊背后的架构考量吗？
    </mstts:express-as>
  </voice>
</speak>
```

---

## 📜 模板二：男女声深情合诵（舒婷《致橡树》节选）

男声（云健，浑厚沉稳）与女声（晓晓，抒情温婉）深情合诵：

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <!-- 男声：云健 -->
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-6%" pitch="-2Hz">
      我如果爱你——<break time="500ms"/>
      绝不像攀援的凌霄花，借你的高枝炫耀自己；<break time="600ms"/>
      我如果爱你——<break time="500ms"/>
      绝不学痴情的鸟儿，为绿荫重复单调的歌曲。<break time="800ms"/>
    </prosody>
  </voice>

  <!-- 女声：晓晓 -->
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="lyrical">
      <prosody rate="-4%" pitch="+2Hz">
        也不止像泉源，常年送来清凉的慰藉；<break time="500ms"/>
        也不止像险峰，增加你的高度，衬托你的威仪。<break time="600ms"/>
        甚至日光，甚至春雨。<break time="700ms"/>
        不，这些都还不够！<break time="500ms"/>
        我必须是你近旁的一株木棉，作为树的形象和你站在一起。<break time="800ms"/>
      </prosody>
    </mstts:express-as>
  </voice>

  <!-- 男声合诵收尾 -->
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-8%" pitch="-2Hz">
      仿佛永远分离，<break time="400ms"/>
      却又终身相依。
    </prosody>
  </voice>
</speak>
```

---

## 🎭 模板三：单角色剧情起伏与情绪三段反转

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-YunyangNeural">
    <!-- 阶段 1: 轻松日常 -->
    <mstts:express-as style="cheerful">
      那天清晨，阳光刚刚洒在窗台上，一切都显得无比安宁。
    </mstts:express-as>

    <break time="600ms"/>

    <!-- 阶段 2: 突发危机 (严肃紧张、降低音调) -->
    <mstts:express-as style="serious" styledegree="1.8">
      <prosody rate="-10%" pitch="-4Hz">
        直到突然，刺耳的警报声划破了长空！<break time="400ms"/>
        雷达屏幕上，一个不明信号正在以极快的速度逼近！
      </prosody>
    </mstts:express-as>

    <break time="800ms"/>

    <!-- 阶段 3: 沉思平静 (放慢、呼吸) -->
    <mstts:express-as style="calm">
      <prosody rate="-12%" pitch="-6Hz">
        所有人都屏住了呼吸，没有人知道，这一刻究竟意味着终结，还是新生。
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
```

---

## 🏛️ 模板四：央视级纪录片旁白 (Documentary)

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="zh-CN-YunjianNeural">
    <prosody rate="-8%" pitch="-5Hz">
      时间，是一切奥秘的注脚。<break time="600ms"/>
      在青藏高原高耸入云的崇山峻岭之中，古老的冰川经历了数万年的沉睡与消融。
      <break time="500ms"/>
      当第一缕季风拂过山脊，生命的故事，便在这片荒原上悄然生根。
    </prosody>
  </voice>
</speak>
```

---

## 🛠️ CLI 执行方式

```bash
# 直接传入 SSML 文件合成
python3 skill/scripts/tts_client.py --ssml-file podcast.xml --output podcast.mp3
```
