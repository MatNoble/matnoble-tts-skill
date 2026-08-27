#!/usr/bin/env python3
"""
Unit tests for TextNormalizer, PronunciationGuard, and ProsodyEngine in tts_client.py
"""

import unittest
import sys
import os

# Add script directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tts_client import (
    preprocess_text,
    validate_directives,
    convert_directives_to_ssml,
    parse_pause,
)

class TestPreprocessor(unittest.TestCase):
    def test_phone_normalization(self):
        # 11-digit mobile
        text, logs = preprocess_text("请拨打电话 13800138000 咨询")
        self.assertIn("[say-as:telephone]13800138000[/say-as]", text)

        # 400 service number
        text2, logs2 = preprocess_text("服务热线：400-123-4567")
        self.assertIn("[say-as:telephone]400-123-4567[/say-as]", text2)

        # Landline with area code
        text3, logs3 = preprocess_text("总机电话 010-88888888")
        self.assertIn("[say-as:telephone]010-88888888[/say-as]", text3)

    def test_digits_normalization(self):
        text, logs = preprocess_text("工号是 9527")
        self.assertIn("[say-as:digits]9527[/say-as]", text)

        text2, logs2 = preprocess_text("验证码 8492")
        self.assertIn("[say-as:digits]8492[/say-as]", text2)

        text3, logs3 = preprocess_text("代号 007")
        self.assertIn("[say-as:digits]007[/say-as]", text3)

        # Quantity / Year / Money should NOT be digits
        text4, logs4 = preprocess_text("2026年一共投入了 5000元 购买 100个 设备")
        self.assertNotIn("[say-as:digits]2026[/say-as]", text4)
        self.assertNotIn("[say-as:digits]5000[/say-as]", text4)
        self.assertNotIn("[say-as:digits]100[/say-as]", text4)

    def test_abbreviation_normalization(self):
        text, logs = preprocess_text("调用 TTS API 接口")
        self.assertIn("[say-as:characters]TTS[/say-as]", text)
        self.assertIn("[say-as:characters]API[/say-as]", text)

        text2, logs2 = preprocess_text("AI 赋能 CPU 与 GPU 协同计算")
        self.assertIn("[say-as:characters]AI[/say-as]", text2)
        self.assertIn("[say-as:characters]CPU[/say-as]", text2)
        self.assertIn("[say-as:characters]GPU[/say-as]", text2)

    def test_date_normalization(self):
        text, logs = preprocess_text("会议定于 2026-08-27 召开")
        self.assertIn("[say-as:date]2026-08-27[/say-as]", text)

    def test_polyphone_guard(self):
        text, logs = preprocess_text("我们需要重新核算这批货物的重量")
        self.assertIn("[sub:chóng]重[/sub]新", text)
        self.assertIn("[sub:zhòng]重[/sub]量", text)

        text2, logs2 = preprocess_text("金融行业的发展行情很好，但他还是决定辞职出差")
        self.assertIn("[sub:háng]行[/sub]业", text2)
        self.assertIn("[sub:háng]行[/sub]情", text2)
        self.assertIn("出[sub:chāi]差[/sub]", text2)

        text3, logs3 = preprocess_text("终于说服了他，买到了这件便宜实惠的衣服")
        self.assertIn("[sub:shuō]说[/sub]服", text3)
        self.assertIn("[sub:pián]便[/sub]宜", text3)

        text4, logs4 = preprocess_text("在西藏这片土地上隐藏着无尽的宝藏")
        self.assertIn("西[sub:zàng]藏[/sub]", text4)
        self.assertIn("隐[sub:cáng]藏[/sub]", text4)
        self.assertIn("宝[sub:zàng]藏[/sub]", text4)

    def test_prosody_injection(self):
        text, logs = preprocess_text("这项技术很强，但是落地成本很高。你觉得呢？", auto_prosody=True)
        self.assertIn("[pause:400ms]但是", text)
        self.assertIn("？[pause:600ms]", text)

        text2, logs2 = preprocess_text("方案看起来很好，然而执行难度极大。不过，更重要的是我们没有放弃！", auto_prosody=True)
        self.assertIn("[pause:400ms]然而", text2)
        self.assertIn("[pause:400ms]不过", text2)
        self.assertIn("[pause:400ms]更重要的是", text2)

        # Default auto_prosody=False should not inject pause
        text3, logs3 = preprocess_text("这项技术很强，但是落地成本很高。你觉得呢？", auto_prosody=False)
        self.assertNotIn("[pause:400ms]但是", text3)
        self.assertNotIn("？[pause:600ms]", text3)

    def test_backward_compatibility(self):
        # Validate directives compatibility
        valid_sample = "大家好[pause:500ms][emphasis:strong]欢迎光临[/emphasis]，[say-as:telephone]13800138000[/say-as]"
        ok, issues = validate_directives(valid_sample)
        self.assertTrue(ok)
        self.assertEqual(len(issues), 0)

        # Convert to SSML compatibility
        ssml = convert_directives_to_ssml(valid_sample, voice="zh-CN-YunxiNeural", speed=1.1)
        self.assertIn('<break time="500ms"/>', ssml)
        self.assertIn('<emphasis level="strong">欢迎光临</emphasis>', ssml)
        self.assertIn('<say-as interpret-as="telephone">13800138000</say-as>', ssml)
        self.assertIn('name="zh-CN-YunxiNeural"', ssml)

        # Preprocess on already-annotated text should not corrupt existing tags
        text, logs = preprocess_text("联系电话 [say-as:telephone]13800138000[/say-as]，请重新核算", auto_prosody=True)
        self.assertIn("[say-as:telephone]13800138000[/say-as]", text)
        self.assertIn("[sub:chóng]重[/sub]新", text)
        ok2, issues2 = validate_directives(text)
        self.assertTrue(ok2)

if __name__ == "__main__":
    unittest.main()
