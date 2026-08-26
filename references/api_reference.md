# REST API 与额度规范详情 (API Reference)

MatNoble-TTS 提供标准符合 OpenAI 音频规范的高性能边缘 HTTP API，支持零门槛公共体验通道与 D1 数据库驱动的多租户配额管理。

---

## 🌐 服务基址与鉴权

- **官方线上基址**：`https://speak.matnoble.top`
- **鉴权方式**（二选一）：
  - `Authorization: Bearer vc_your_api_key`
  - `X-API-Key: vc_your_api_key`
- **免 Key 公共通道**：若请求头中未包含任何 Key，服务端将自动分配至**公共体验通道**（单次 ≤ 500 字，每日全局共享 200 次配额）。

---

## 🔌 核心端点

### 1. 文字转语音 (TTS)
- **路径**：`POST /v1/audio/speech`
- **Content-Type**：`application/json`

#### 普通模式请求体 (JSON)：
```json
{
  "input": "大家好，欢迎使用 MatNoble-TTS 语音服务。",
  "voice": "zh-CN-XiaoxiaoNeural",
  "speed": 1.0,
  "pitch": "0",
  "volume": "0",
  "style": "general"
}
```

#### SSML 模式请求体 (JSON)：
```json
{
  "format": "ssml",
  "ssml": "<speak version=\"1.0\" ...>...</speak>"
}
```

#### 响应说明：
- **状态码**：`200 OK`
- **Content-Type**：`audio/mpeg`
- **响应体**：纯二进制 MP3 音频数据流。
- **响应头**（包含实时额度流控）：
  - `X-RateLimit-Limit`: 今日总调用上限
  - `X-RateLimit-Remaining`: 今日剩余可用次数
  - `X-RateLimit-Reset`: 今日重置的 UTC 时间戳（秒）

### 2. 用量与额度查询
- **路径**：`GET /v1/api/usage`

#### 响应示例 (JSON)：
```json
{
  "daily_limit": 200,
  "used_today": 12,
  "remaining": 188,
  "date": "2026-08-26",
  "name": "公共免 Key 体验通道",
  "is_public_demo": true
}
```

---

## ⚠️ 常见状态码与错误处理

| 状态码 | 错误码 (`code`) | 错误原因 | 建议处理策略 |
| :--- | :--- | :--- | :--- |
| `400` | `text_too_long` | 公共体验通道单次文本超过 500 字 | 建议拆分文本段落，或配置专属 Key |
| `400` | `ssml_too_long` | SSML 文本体积超过 8KB | 缩减 SSML 内容长度 |
| `401` | `auth_error` | API Key 无效或格式不正确 | 检查并重新填入正确的 `vc_...` Key |
| `403` | `key_required` | 批量上传等操作未带 Key | 在设置中配置专属 Key 后重试 |
| `429` | `auth_error` | 今日调用次数已达上限 | 提示用户次日恢复或联系作者获取更大配额 |
| `500` | `edge_tts_error`| 微软上游或网络异常 | 检查文本是否含有非法特殊符号，并在 1 秒后重试 |
