#!/usr/bin/env python3
"""
MatNoble-TTS Standard Client & Audio Script Utility
Zero third-party dependencies (pure Python standard library).
Designed for AI Agents and CLI workflows.
"""

import sys
import os
import argparse
import json
import re
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any, Tuple

DEFAULT_ENDPOINT = "https://speak.matnoble.top"
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
MAX_PUBLIC_CHARS = 500

# ----------------------------------------------------------------------
# Directive to SSML Converter & Validator
# ----------------------------------------------------------------------

SAFE_EMPHASIS = {"reduced", "moderate", "strong", "x-strong"}
SAFE_SAY_AS = {"digits", "telephone", "date", "characters"}
SAFE_RATE = {"x-slow", "slow", "medium", "fast", "x-fast"}

def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))

def parse_pause(val: str) -> Optional[int]:
    val = val.strip().lower()
    named = {"none": 0, "x-weak": 100, "weak": 200, "medium": 400, "strong": 800, "x-strong": 1200}
    if val in named:
        return named[val]
    m_ms = re.match(r"^(\d+)ms$", val)
    if m_ms:
        return int(m_ms.group(1))
    m_s = re.match(r"^(\d+(?:\.\d+)?)s$", val)
    if m_s:
        return int(float(m_s.group(1)) * 1000)
    return None

def validate_directives(text: str) -> Tuple[bool, list]:
    """Validate syntax of inline directives in text."""
    issues = []
    marker_re = re.compile(r"\[/?(pause|emphasis|rate|pitch|volume|style|say-as|sub)(?::([^\]]*))?\]", re.IGNORECASE)
    stack = []
    total_pause_ms = 0
    directive_count = 0

    for match in marker_re.finditer(text):
        raw = match.group(0)
        is_close = raw.startswith("[/")
        name = match.group(1).lower()
        arg = (match.group(2) or "").strip()

        directive_count += 1
        if directive_count > 50:
            issues.append("警告：行内指令数量超过推荐上限 50 个。")

        if is_close:
            if not stack:
                issues.append(f"语法错误：未匹配的闭合标签 '{raw}' 在位置 {match.start()}。")
            else:
                last_open = stack.pop()
                if last_open != name:
                    issues.append(f"语法错误：标签嵌套不匹配，期望 '[/{last_open}]'，实际出现 '{raw}'。")
        else:
            if name == "pause":
                ms = parse_pause(arg if arg else "medium")
                if ms is None:
                    issues.append(f"语法错误：无效的停顿参数 '{arg}'。")
                elif ms > 5000:
                    issues.append(f"停顿过长：单次停顿不得超过 5000ms (当前 {ms}ms)。")
                else:
                    total_pause_ms += ms
            else:
                if name == "emphasis" and arg and arg.lower() not in SAFE_EMPHASIS:
                    issues.append(f"参数提示：emphasis 等级建议为 reduced/moderate/strong/x-strong (当前为 '{arg}')。")
                elif name == "say-as" and arg and arg.lower() not in SAFE_SAY_AS:
                    issues.append(f"参数提示：say-as 类型建议为 digits/telephone/date/characters (当前为 '{arg}')。")
                stack.append(name)

    while stack:
        missing = stack.pop()
        issues.append(f"语法错误：标签 '[{missing}]' 未正确闭合，缺少 '[/{missing}]'。")

    if total_pause_ms > 30000:
        issues.append(f"停顿警告：累计停顿时间已超过 30 秒 ({total_pause_ms}ms)。")

    return (len(issues) == 0, issues)

def convert_directives_to_ssml(text: str, voice: str = DEFAULT_VOICE, speed: float = 1.0, pitch: str = "0", style: str = "general") -> str:
    """Convert text with inline directives into full standard W3C/MS SSML."""
    body = ""
    i = 0
    marker_re = re.compile(r"\[(pause|emphasis|rate|pitch|volume|style|say-as|sub)(?::([^\]]*))?\]", re.IGNORECASE)

    def find_close(open_name: str, start_idx: int) -> Optional[Tuple[int, int]]:
        scanner = re.compile(r"\[/?(pause|emphasis|rate|pitch|volume|style|say-as|sub)(?::([^\]]*))?\]", re.IGNORECASE)
        scanner_pos = start_idx
        depth = 1
        while True:
            m = scanner.search(text, scanner_pos)
            if not m:
                return None
            m_raw = m.group(0)
            m_is_close = m_raw.startswith("[/")
            m_name = m.group(1).lower()
            scanner_pos = m.end()

            if m_name == open_name:
                if m_is_close:
                    depth -= 1
                    if depth == 0:
                        return (m.start(), m.end())
                else:
                    depth += 1

    while i < len(text):
        m = marker_re.search(text, i)
        if not m:
            body += escape_xml(text[i:])
            break

        body += escape_xml(text[i:m.start()])
        name = m.group(1).lower()
        arg = (m.group(2) or "").strip()

        if name == "pause":
            ms = parse_pause(arg if arg else "medium")
            if ms is not None and ms <= 5000:
                body += f'<break time="{ms}ms"/>'
            else:
                body += escape_xml(m.group(0))
            i = m.end()
        else:
            close_info = find_close(name, m.end())
            if close_info:
                close_start, close_end = close_info
                inner_text = text[m.end():close_start]
                inner_converted = escape_xml(inner_text)

                if name == "emphasis":
                    level = arg if arg.lower() in SAFE_EMPHASIS else "strong"
                    body += f'<emphasis level="{level}">{inner_converted}</emphasis>'
                elif name == "rate":
                    body += f'<prosody rate="{escape_xml(arg)}">{inner_converted}</prosody>'
                elif name == "pitch":
                    body += f'<prosody pitch="{escape_xml(arg)}">{inner_converted}</prosody>'
                elif name == "volume":
                    body += f'<prosody volume="{escape_xml(arg)}">{inner_converted}</prosody>'
                elif name == "say-as":
                    interpret_as = arg if arg.lower() in SAFE_SAY_AS else "digits"
                    body += f'<say-as interpret-as="{interpret_as}">{inner_converted}</say-as>'
                elif name == "sub":
                    body += f'<sub alias="{escape_xml(arg)}">{inner_converted}</sub>'
                elif name == "style":
                    parts = arg.split(":")
                    st_name = parts[0].strip() if parts else "general"
                    degree = parts[1].strip() if len(parts) > 1 else "1.5"
                    body += f'<mstts:express-as style="{escape_xml(st_name)}" styledegree="{escape_xml(degree)}">{inner_converted}</mstts:express-as>'
                i = close_end
            else:
                body += escape_xml(m.group(0))
                i = m.end()

    # Wrap in voice & prosody
    rate_pct = f"{int((speed - 1.0) * 100):+d}%" if speed != 1.0 else None
    pitch_val = f"{int(pitch):+d}Hz" if pitch not in ("0", "") else None

    inner_xml = body
    if rate_pct or pitch_val:
        attrs = []
        if rate_pct: attrs.append(f'rate="{rate_pct}"')
        if pitch_val: attrs.append(f'pitch="{pitch_val}"')
        inner_xml = f'<prosody {" ".join(attrs)}>{inner_xml}</prosody>'

    if style and style != "general":
        inner_xml = f'<mstts:express-as style="{escape_xml(style)}">{inner_xml}</mstts:express-as>'

    xml_lang = "zh-CN"
    if voice.startswith("en-"): xml_lang = "en-US"
    elif voice.startswith("ja-"): xml_lang = "ja-JP"
    elif voice.startswith("ko-"): xml_lang = "ko-KR"
    elif voice.startswith("es-"): xml_lang = "es-ES"
    elif voice.startswith("fr-"): xml_lang = "fr-FR"

    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{xml_lang}">\n'
        f'  <voice name="{voice}">\n'
        f'    {inner_xml}\n'
        f'  </voice>\n'
        f'</speak>'
    )
    return ssml


# ----------------------------------------------------------------------
# HTTP API Calls
# ----------------------------------------------------------------------

def call_api(endpoint: str, path: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, data: Optional[bytes] = None) -> Tuple[int, Dict[str, str], bytes]:
    url = endpoint.rstrip("/") + path
    req = urllib.request.Request(url, data=data, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_headers = {k.lower(): v for k, v in resp.getheaders()}
            return resp.status, resp_headers, resp.read()
    except urllib.error.HTTPError as e:
        resp_headers = {k.lower(): v for k, v in e.headers.items()}
        return e.code, resp_headers, e.read()
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络连接异常：无法连接至服务端 '{url}' ({e.reason})")

def check_usage(endpoint: str, api_key: str):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    status, resp_headers, body = call_api(endpoint, "/v1/api/usage", "GET", headers)
    if status == 200:
        data = json.loads(body.decode("utf-8"))
        is_public = data.get("is_public_demo", False)
        print("=== MatNoble-TTS 额度状态 ===")
        print(f"服务地址: {endpoint}")
        print(f"通道模式: {'公共免 Key 体验通道' if is_public else '专属 API Key (' + str(data.get('name', '')) + ')'}")
        print(f"今日剩余: {data.get('remaining')} / {data.get('daily_limit')} 次")
        print(f"今日已用: {data.get('used_today')} 次")
        print(f"统计日期: {data.get('date')}")
        if is_public:
            print("\n提示: 公共通道单次文本上限 500 字。如需长文本与独立配额，可访问 https://matnoble.top 获取专属 Key。")
    else:
        try:
            err = json.loads(body.decode("utf-8"))
            msg = err.get("error", {}).get("message", body.decode("utf-8"))
        except Exception:
            msg = body.decode("utf-8")
        print(f"查询失败 (HTTP {status}): {msg}", file=sys.stderr)
        sys.exit(1)

def synthesize_speech(
    endpoint: str,
    api_key: str,
    text: Optional[str] = None,
    ssml: Optional[str] = None,
    voice: str = DEFAULT_VOICE,
    speed: float = 1.0,
    pitch: str = "0",
    volume: str = "0",
    style: str = "general",
    output_file: str = "output.mp3"
):
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if ssml:
        payload = {
            "format": "ssml",
            "ssml": ssml
        }
    else:
        if not text:
            raise ValueError("必须提供合成文本 (--text 或 --file) 或 SSML (--ssml 或 --ssml-file)")
        payload = {
            "input": text,
            "voice": voice,
            "speed": speed,
            "pitch": pitch,
            "volume": volume,
            "style": style
        }

    post_data = json.dumps(payload).encode("utf-8")
    status, resp_headers, body = call_api(endpoint, "/v1/audio/speech", "POST", headers, post_data)

    if status == 200:
        with open(output_file, "wb") as f:
            f.write(body)
        rem = resp_headers.get("x-ratelimit-remaining", "未知")
        limit = resp_headers.get("x-ratelimit-limit", "未知")
        size_kb = len(body) / 1024
        print(f"✔ 语音合成成功！已保存至: {output_file} ({size_kb:.1f} KB)")
        print(f"ℹ 剩余可用额度: {rem} / {limit} 次")
    else:
        try:
            err = json.loads(body.decode("utf-8"))
            msg = err.get("error", {}).get("message", body.decode("utf-8"))
        except Exception:
            msg = body.decode("utf-8")
        print(f"✖ 合成失败 (HTTP {status}): {msg}", file=sys.stderr)
        if status == 429:
            print("💡 建议：今日额度已用尽。可在设置中更换专属 Key，或明日重试。", file=sys.stderr)
        elif status == 400 and "单次文本上限" in msg:
            print("💡 建议：公共通道单次限制 500 字，请使用分段合成或配置专属 Key。", file=sys.stderr)
        sys.exit(1)


# ----------------------------------------------------------------------
# CLI Entrypoint
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MatNoble-TTS Client & Audio Scripting Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例用法:
  # 1. 基础合成 (直接试用公共通道)
  python3 tts_client.py --text "你好，世界！" --output hello.mp3

  # 2. 带语音指令的自然修饰合成
  python3 tts_client.py --text "大家好[pause:500ms][emphasis:strong]欢迎体验[/emphasis]智能配音服务。" --output demo.mp3

  # 3. 本地预览并验证转换为标准 SSML
  python3 tts_client.py --to-ssml --text "转折前稍作停顿[pause:600ms]然后继续讲述。"

  # 4. 检查指令语法
  python3 tts_client.py --validate --text "未闭合标签[emphasis:strong]测试文本"

  # 5. 查询剩余额度
  python3 tts_client.py --check-usage
"""
    )

    parser.add_argument("--endpoint", default=os.getenv("MATNOBLE_TTS_ENDPOINT", DEFAULT_ENDPOINT), help="MatNoble-TTS 服务地址")
    parser.add_argument("--api-key", default=os.getenv("MATNOBLE_TTS_API_KEY", ""), help="API Key (留空使用公共体验通道)")
    parser.add_argument("--text", help="要合成的文本（支持行内指令 [pause], [emphasis] 等）")
    parser.add_argument("--file", help="读取文本文件的路径")
    parser.add_argument("--ssml", help="标准 SSML 字符串")
    parser.add_argument("--ssml-file", help="标准 SSML 文件路径")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"音色名称 (默认: {DEFAULT_VOICE})")
    parser.add_argument("--speed", type=float, default=1.0, help="语速倍率 0.5 - 2.0 (默认: 1.0)")
    parser.add_argument("--pitch", default="0", help="音调偏移 Hz，如 +10, -10 (默认: 0)")
    parser.add_argument("--volume", default="0", help="音量偏移 (默认: 0)")
    parser.add_argument("--style", default="general", help="情感风格 (如 cheerful, serious, calm 等)")
    parser.add_argument("--output", "-o", default="output.mp3", help="输出音频文件路径 (默认: output.mp3)")
    parser.add_argument("--check-usage", action="store_true", help="查询当前 Key 或公共通道的配额用量")
    parser.add_argument("--to-ssml", action="store_true", help="仅将文本与行内指令转为标准 SSML 打印输出，不发请求")
    parser.add_argument("--validate", action="store_true", help="验证文本内语音指令的闭合性与参数合法性")

    args = parser.parse_args()

    # 1. 检查配额
    if args.check_usage:
        check_usage(args.endpoint, args.api_key)
        return

    # 提取输入文本
    raw_text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_text = f.read()

    # 提取 SSML
    raw_ssml = args.ssml
    if args.ssml_file:
        with open(args.ssml_file, "r", encoding="utf-8") as f:
            raw_ssml = f.read()

    # 2. 校验指令
    if args.validate:
        if not raw_text:
            print("错误：请提供要验证的文本 (--text 或 --file)", file=sys.stderr)
            sys.exit(1)
        ok, issues = validate_directives(raw_text)
        if ok:
            print("✔ 语音指令语法校验通过！无未闭合标签或异常参数。")
        else:
            print("✖ 发现以下指令问题：", file=sys.stderr)
            for issue in issues:
                print(f"  • {issue}", file=sys.stderr)
            sys.exit(1)
        return

    # 3. 转换为 SSML 打印
    if args.to_ssml:
        if not raw_text:
            print("错误：请提供要转换的文本 (--text 或 --file)", file=sys.stderr)
            sys.exit(1)
        ssml_output = convert_directives_to_ssml(raw_text, args.voice, args.speed, args.pitch, args.style)
        print(ssml_output)
        return

    # 4. 执行音频合成
    if not raw_text and not raw_ssml:
        parser.print_help()
        sys.exit(1)

    synthesize_speech(
        endpoint=args.endpoint,
        api_key=args.api_key,
        text=raw_text,
        ssml=raw_ssml,
        voice=args.voice,
        speed=args.speed,
        pitch=args.pitch,
        volume=args.volume,
        style=args.style,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
