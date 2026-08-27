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
from typing import Optional, Dict, Any, Tuple, List

DEFAULT_ENDPOINT = "https://speak.matnoble.top"
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
MAX_PUBLIC_CHARS = 500

# ----------------------------------------------------------------------
# Text Preprocessing & Audio Director Pipeline (Zero Dependencies)
# ----------------------------------------------------------------------

class DirectiveMasker:
    """Helper to protect existing directives/tags from being mutated by subsequent regex steps."""

    PAIRED_TAG_RE = re.compile(r"\[([a-zA-Z0-9_-]+)(?::[^\]]*)?\].*?\[/\1\]", re.DOTALL)
    SINGLE_TAG_RE = re.compile(r"\[[a-zA-Z0-9_-]+(?::[^\]]*)?\]")

    @classmethod
    def mask(cls, text: str, existing_placeholders: Optional[Dict[str, str]] = None) -> Tuple[str, Dict[str, str]]:
        placeholders = existing_placeholders if existing_placeholders is not None else {}
        idx = len(placeholders)

        def repl(m):
            nonlocal idx
            ph = f"dirtag_{idx}"
            idx += 1
            placeholders[ph] = m.group(0)
            return ph

        text = cls.PAIRED_TAG_RE.sub(repl, text)
        text = cls.SINGLE_TAG_RE.sub(repl, text)
        return text, placeholders

    @classmethod
    def unmask(cls, text: str, placeholders: Dict[str, str]) -> str:
        prev = None
        while prev != text:
            prev = text
            for ph, original in placeholders.items():
                text = text.replace(ph, original)
        return text


class TextNormalizer:
    """Non-Standard Words (NSW) Normalizer for Chinese TTS (inspired by PaddleSpeech)."""

    PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9}|(?:0\d{2,3}-?)?\d{7,8}|(?:400|800)[-\s]?\d{3,4}[-\s]?\d{3,4}|(?:400|800)\d{7})(?!\d)")
    DIGITS_CONTEXT_RE = re.compile(r"((?:工号|编号|代号|验证码|密码|账号|座机|房间号|单号|订单号|卡号|QQ号?|号码)[是为：:\s]{0,3})(\d{2,12})(?!\d)")
    LEADING_ZERO_RE = re.compile(r"(?<!\d)(0\d{1,8})(?!\d)")
    STANDALONE_DIGITS_RE = re.compile(r"(?<![\d¥￥$€£])(\d{4,6})(?!\d)(?![0-9年月日号元块个只位次人张台条套件点分秒米克倍%％度本首篇幅间户层幢座架艘辆袋盒瓶桶折])")
    
    ACRONYM_RE = re.compile(r"(?<![a-zA-Z0-9])([A-Z]{2,6})(?![a-zA-Z0-9])")
    CURRENCY_RE = re.compile(r"[¥￥](\d+(?:\.\d+)?)\s*")
    PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[%％]")
    DATE_RE = re.compile(r"(?<!\d)((?:19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2})(?!\d)")

    ACRONYMS = {
        "API", "TTS", "AI", "SDK", "CPU", "GPU", "URL", "LLM", "HTTP", "HTTPS",
        "REST", "JSON", "UI", "UX", "ID", "OS", "APP", "IP", "DNS", "VIP", "VVIP",
        "K8S", "GPT", "AGI", "NLP", "CV", "ASR", "OCR", "RAG", "SLA", "CDN",
        "SSML", "NSW", "CLI", "IDE", "GUI", "NPM", "CI", "CD", "TCP", "UDP",
        "VPN", "SSH", "SSL", "TLS", "RAM", "ROM", "SSD", "HDD", "USB", "PDF",
        "PPT", "DOC", "DOCX", "WIFI", "CEO", "CTO", "CFO", "COO", "HR", "PR",
        "OK", "KOL", "KOC", "B2B", "B2C", "SaaS", "PaaS", "IaaS", "CRM", "ERP",
        "OA", "SQL", "HTML", "CSS", "JS", "TS", "PHP"
    }

    NUM_MAP = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
               '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}

    @classmethod
    def normalize(cls, text: str) -> Tuple[str, List[str]]:
        logs = []

        def replace_currency(m):
            logs.append(f"NSW 货币: {m.group(0)} -> {m.group(1)}元")
            return f"{m.group(1)}元"
        text = cls.CURRENCY_RE.sub(replace_currency, text)

        def replace_percent(m):
            num_str = m.group(1)
            parts = num_str.split('.')
            int_part = cls._int_to_zh(int(parts[0]))
            if len(parts) > 1:
                dec_part = ''.join(cls.NUM_MAP.get(c, c) for c in parts[1])
                zh_val = f"百分之{int_part}点{dec_part}"
            else:
                zh_val = f"百分之{int_part}"
            logs.append(f"NSW 百分比: {m.group(0)} -> {zh_val}")
            return zh_val
        text = cls.PERCENT_RE.sub(replace_percent, text)

        def replace_phone(m):
            logs.append(f"NSW 电话: {m.group(1)} -> [say-as:telephone]{m.group(1)}[/say-as]")
            return f"[say-as:telephone]{m.group(1)}[/say-as]"
        text = cls.PHONE_RE.sub(replace_phone, text)

        def replace_date(m):
            logs.append(f"NSW 日期: {m.group(1)} -> [say-as:date]{m.group(1)}[/say-as]")
            return f"[say-as:date]{m.group(1)}[/say-as]"
        text = cls.DATE_RE.sub(replace_date, text)

        masked, phs = DirectiveMasker.mask(text)

        def replace_acronym(m):
            word = m.group(1)
            if word in cls.ACRONYMS or (len(word) >= 2 and word.isupper() and word not in {"THE", "AND", "FOR", "WITH", "THIS", "THAT", "FROM", "HAVE", "ARE", "YOU", "NOT"}):
                logs.append(f"NSW 缩写: {word} -> [say-as:characters]{word}[/say-as]")
                masked_tag, _ = DirectiveMasker.mask(f"[say-as:characters]{word}[/say-as]", phs)
                return masked_tag
            return word
        masked = cls.ACRONYM_RE.sub(replace_acronym, masked)

        def replace_context_digits(m):
            prefix = m.group(1)
            num = m.group(2)
            logs.append(f"NSW 数字串: {num} -> [say-as:digits]{num}[/say-as]")
            masked_tag, _ = DirectiveMasker.mask(f"[say-as:digits]{num}[/say-as]", phs)
            return f"{prefix}{masked_tag}"
        masked = cls.DIGITS_CONTEXT_RE.sub(replace_context_digits, masked)

        def replace_leading_zero(m):
            num = m.group(1)
            logs.append(f"NSW 数字串: {num} -> [say-as:digits]{num}[/say-as]")
            masked_tag, _ = DirectiveMasker.mask(f"[say-as:digits]{num}[/say-as]", phs)
            return masked_tag
        masked = cls.LEADING_ZERO_RE.sub(replace_leading_zero, masked)

        def replace_standalone_digits(m):
            num = m.group(1)
            logs.append(f"NSW 数字串: {num} -> [say-as:digits]{num}[/say-as]")
            masked_tag, _ = DirectiveMasker.mask(f"[say-as:digits]{num}[/say-as]", phs)
            return masked_tag
        masked = cls.STANDALONE_DIGITS_RE.sub(replace_standalone_digits, masked)

        text = DirectiveMasker.unmask(masked, phs)
        return text, logs

    @classmethod
    def _int_to_zh(cls, n: int) -> str:
        if n == 0: return '零'
        units = ['', '十', '百', '千', '万']
        digits = '零一二三四五六七八九'
        s = str(n)
        l = len(s)
        if l == 2 and s[0] == '1':
            return '十' + (digits[int(s[1])] if s[1] != '0' else '')
        res = []
        for i, c in enumerate(s):
            d = int(c)
            pos = l - i - 1
            if d != 0:
                res.append(digits[d] + units[pos])
            else:
                if not res or res[-1] != '零':
                    res.append('零')
        zh = ''.join(res).rstrip('零')
        return zh


class PronunciationGuard:
    """Polyphone Disambiguation and Pronunciation Guard (110+ high-frequency entries)."""

    POLYPHONE_MAP = {
        # 重 (chóng vs zhòng)
        "重新": "[sub:chóng]重[/sub]新",
        "重申": "[sub:chóng]重[/sub]申",
        "重阳": "[sub:chóng]重[/sub]阳",
        "重演": "[sub:chóng]重[/sub]演",
        "重逢": "[sub:chóng]重[/sub]逢",
        "重复": "[sub:chóng]重[/sub]复",
        "重叠": "[sub:chóng]重[/sub]叠",
        "重组": "[sub:chóng]重[/sub]组",
        "重庆": "[sub:chóng]重[/sub]庆",
        "重温": "[sub:chóng]重[/sub]温",
        "重整旗鼓": "[sub:chóng]重[/sub]整旗鼓",
        "重见天日": "[sub:chóng]重[/sub]见天日",
        "重出江湖": "[sub:chóng]重[/sub]出江湖",
        "重修旧好": "[sub:chóng]重[/sub]修旧好",
        "重蹈覆辙": "[sub:chóng]重[/sub]蹈覆辙",
        "重获新生": "[sub:chóng]重[/sub]获新生",
        "重量": "[sub:zhòng]重[/sub]量",
        "重心": "[sub:zhòng]重[/sub]心",
        "沉重": "沉[sub:zhòng]重[/sub]",
        "重视": "[sub:zhòng]重[/sub]视",
        "重负": "[sub:zhòng]重[/sub]负",
        "慎重": "慎[sub:zhòng]重[/sub]",
        "举足轻重": "举足轻[sub:zhòng]重[/sub]",

        # 行 (háng vs xíng)
        "行业": "[sub:háng]行[/sub]业",
        "银行": "银[sub:háng]行[/sub]",
        "行规": "[sub:háng]行[/sub]规",
        "同行": "同[sub:háng]行[/sub]",
        "行情": "[sub:háng]行[/sub]情",
        "行列": "[sub:háng]行[/sub]列",
        "行家": "[sub:háng]行[/sub]家",
        "内行": "内[sub:háng]行[/sub]",
        "外行": "外[sub:háng]行[/sub]",
        "这一行": "这一[sub:háng]行[/sub]",
        "行走": "[sub:xíng]行[/sub]走",
        "行动": "[sub:xíng]行[/sub]动",
        "行程": "[sub:xíng]行[/sub]程",
        "执行": "执[sub:xíng]行[/sub]",
        "行为": "[sub:xíng]行[/sub]为",
        "履行": "履[sub:xíng]行[/sub]",
        "流行": "流[sub:xíng]行[/sub]",
        "旅行": "旅[sub:xíng]行[/sub]",
        "举行": "举[sub:xíng]行[/sub]",

        # 差 (chāi vs chà vs chā vs cī)
        "出差": "出[sub:chāi]差[/sub]",
        "差事": "[sub:chāi]差[/sub]事",
        "公差": "公[sub:chāi]差[/sub]",
        "差使": "[sub:chāi]差[/sub]使",
        "差距": "[sub:chā]差[/sub]距",
        "差别": "[sub:chā]差[/sub]别",
        "差异": "[sub:chā]差[/sub]异",
        "偏差": "偏[sub:chā]差[/sub]",
        "差错": "[sub:chā]差[/sub]错",
        "差劲": "[sub:chà]差[/sub]劲",
        "差不多": "[sub:chà]差[/sub]不多",
        "差点": "[sub:chà]差[/sub]点",
        "参差": "参[sub:cī]差[/sub]",
        "参差不齐": "参[sub:cī]差[/sub]不齐",

        # 藏 (zàng vs cáng)
        "西藏": "西[sub:zàng]藏[/sub]",
        "宝藏": "宝[sub:zàng]藏[/sub]",
        "藏文": "[sub:zàng]藏[/sub]文",
        "藏族": "[sub:zàng]藏[/sub]族",
        "藏经阁": "[sub:zàng]藏[/sub]经阁",
        "青藏": "青[sub:zàng]藏[/sub]",
        "隐藏": "隐[sub:cáng]藏[/sub]",
        "躲藏": "躲[sub:cáng]藏[/sub]",
        "收藏": "收[sub:cáng]藏[/sub]",
        "蕴藏": "蕴[sub:cáng]藏[/sub]",
        "储藏": "储[sub:cáng]藏[/sub]",

        # 说 (shuō vs shuì)
        "说服": "[sub:shuō]说[/sub]服",
        "游说": "游[sub:shuì]说[/sub]",

        # 便 (pián vs biàn)
        "便宜": "[sub:pián]便[/sub]宜",
        "大腹便便": "大腹[sub:pián]便[/sub][sub:pián]便[/sub]",
        "方便": "方[sub:biàn]便[/sub]",
        "便利": "[sub:biàn]便[/sub]利",
        "便民": "[sub:biàn]便[/sub]民",
        "随便": "随[sub:biàn]便[/sub]",
        "便捷": "[sub:biàn]便[/sub]捷",
        "便当": "[sub:biàn]便[/sub]当",

        # 处 (chǔ vs chù)
        "处理": "[sub:chǔ]处[/sub]理",
        "处于": "[sub:chǔ]处[/sub]于",
        "处置": "[sub:chǔ]处[/sub]置",
        "处境": "[sub:chǔ]处[/sub]境",
        "处分": "[sub:chǔ]处[/sub]分",
        "相处": "相[sub:chǔ]处[/sub]",
        "惩处": "惩[sub:chǔ]处[/sub]",
        "到处": "到[sub:chù]处[/sub]",
        "处所": "[sub:chù]处[/sub]所",
        "长处": "长[sub:chù]处[/sub]",
        "好处": "好[sub:chù]处[/sub]",
        "办事处": "办事[sub:chù]处[/sub]",

        # 长 (cháng vs zhǎng)
        "长度": "[sub:cháng]长[/sub]度",
        "长短": "[sub:cháng]长[/sub]短",
        "长江": "[sub:cháng]长[/sub]江",
        "长远": "[sub:cháng]长[/sub]远",
        "漫长": "漫[sub:cháng]长[/sub]",
        "特长": "特[sub:cháng]长[/sub]",
        "生长": "生[sub:zhǎng]长[/sub]",
        "增长": "增[sub:zhǎng]长[/sub]",
        "长辈": "[sub:zhǎng]长[/sub]辈",
        "厂长": "厂[sub:zhǎng]长[/sub]",
        "市长": "市[sub:zhǎng]长[/sub]",
        "校长": "校[sub:zhǎng]长[/sub]",
        "院长": "院[sub:zhǎng]长[/sub]",
        "董事长": "董事[sub:zhǎng]长[/sub]",

        # 调 (tiáo vs diào)
        "调节": "[sub:tiáo]调[/sub]节",
        "调整": "[sub:tiáo]调[/sub]整",
        "协调": "协[sub:tiáo]调[/sub]",
        "调和": "[sub:tiáo]调[/sub]和",
        "调配": "[sub:tiáo]调[/sub]配",
        "调查": "[sub:diào]调[/sub]查",
        "调研": "[sub:diào]调[/sub]研",
        "调动": "[sub:diào]调[/sub]动",
        "调遣": "[sub:diào]调[/sub]遣",
        "音调": "音[sub:diào]调[/sub]",
        "声调": "声[sub:diào]调[/sub]",
        "强调": "强[sub:diào]调[/sub]",
        "情调": "情[sub:diào]调[/sub]",

        # 乐 (yuè vs lè)
        "音乐": "音[sub:yuè]乐[/sub]",
        "乐器": "[sub:yuè]乐[/sub]器",
        "乐队": "[sub:yuè]乐[/sub]队",
        "乐曲": "[sub:yuè]乐[/sub]曲",
        "奏乐": "奏[sub:yuè]乐[/sub]",
        "快乐": "快[sub:lè]乐[/sub]",
        "乐观": "[sub:lè]乐[/sub]观",
        "乐趣": "[sub:lè]乐[/sub]趣",
        "娱乐": "娱[sub:lè]乐[/sub]",

        # 发 (fà vs fā)
        "头发": "头[sub:fà]发[/sub]",
        "理发": "理[sub:fà]发[/sub]",
        "假发": "假[sub:fà]发[/sub]",
        "短发": "短[sub:fà]发[/sub]",
        "长发": "长[sub:fà]发[/sub]",
        "白发": "白[sub:fà]发[/sub]",
        "毛发": "毛[sub:fà]发[/sub]",
        "发生": "[sub:fā]发[/sub]生",
        "发现": "[sub:fā]发[/sub]现",
        "发展": "[sub:fā]发[/sub]展",
        "发挥": "[sub:fā]发[/sub]挥",
        "发送": "[sub:fā]发[/sub]送",

        # 传 (zhuàn vs chuán)
        "传记": "[sub:zhuàn]传[/sub]记",
        "自传": "自[sub:zhuàn]传[/sub]",
        "评传": "评[sub:zhuàn]传[/sub]",
        "外传": "外[sub:zhuàn]传[/sub]",
        "水浒传": "水浒[sub:zhuàn]传[/sub]",
        "传统": "[sub:chuán]传[/sub]统",
        "传递": "[sub:chuán]传[/sub]递",
        "传送": "[sub:chuán]传[/sub]送",
        "宣传": "宣[sub:chuán]传[/sub]",
        "流传": "流[sub:chuán]传[/sub]",

        # 假 (jià vs jiǎ)
        "假期": "[sub:jià]假[/sub]期",
        "放假": "放[sub:jià]假[/sub]",
        "请假": "请[sub:jià]假[/sub]",
        "休假": "休[sub:jià]假[/sub]",
        "节假日": "节[sub:jià]假[/sub]日",
        "假装": "[sub:jiǎ]假[/sub]装",
        "假设": "[sub:jiǎ]假[/sub]设",
        "假话": "[sub:jiǎ]假[/sub]话",
        "虚假": "虚[sub:jiǎ]假[/sub]",
        "真假": "真[sub:jiǎ]假[/sub]",

        # 降 (jiàng vs xiáng)
        "降落": "[sub:jiàng]降[/sub]落",
        "下降": "下[sub:jiàng]降[/sub]",
        "降低": "[sub:jiàng]降[/sub]低",
        "降价": "[sub:jiàng]降[/sub]价",
        "投降": "投[sub:xiáng]降[/sub]",
        "降服": "[sub:xiáng]降[/sub]服",
        "劝降": "劝[sub:xiáng]降[/sub]",

        # 弹 (tán vs dàn)
        "弹琴": "[sub:tán]弹[/sub]琴",
        "弹奏": "[sub:tán]弹[/sub]奏",
        "弹力": "[sub:tán]弹[/sub]力",
        "弹性": "[sub:tán]弹[/sub]性",
        "反弹": "反[sub:tán]弹[/sub]",
        "子弹": "子[sub:dàn]弹[/sub]",
        "导弹": "导[sub:dàn]弹[/sub]",
        "炮弹": "炮[sub:dàn]弹[/sub]",
        "炸弹": "炸[sub:dàn]弹[/sub]",
        "弹头": "[sub:dàn]弹[/sub]头",

        # 朝 (cháo vs zhāo)
        "朝代": "[sub:cháo]朝[/sub]代",
        "朝向": "[sub:cháo]朝[/sub]向",
        "朝廷": "[sub:cháo]朝[/sub]廷",
        "唐朝": "唐[sub:cháo]朝[/sub]",
        "清朝": "清[sub:cháo]朝[/sub]",
        "明朝": "明[sub:cháo]朝[/sub]",
        "朝夕": "[sub:zhāo]朝[/sub]夕",
        "朝阳": "[sub:zhāo]朝[/sub]阳",
        "朝气": "[sub:zhāo]朝[/sub]气",
        "朝思暮想": "[sub:zhāo]朝[/sub]思暮想",

        # 载 (zài vs zǎi)
        "载重": "[sub:zài]载[/sub]重",
        "装载": "装[sub:zài]载[/sub]",
        "载体": "[sub:zài]载[/sub]体",
        "承载": "承[sub:zài]载[/sub]",
        "满载": "满[sub:zài]载[/sub]",
        "载客": "[sub:zài]载[/sub]客",
        "运载": "运[sub:zài]载[/sub]",
        "记载": "记[sub:zǎi]载[/sub]",
        "登载": "登[sub:zǎi]载[/sub]",
        "刊载": "刊[sub:zǎi]载[/sub]",
        "千载难逢": "千[sub:zǎi]载[/sub]难逢",
        "三年五载": "三年五[sub:zǎi]载[/sub]",

        # 累 (lèi vs léi vs lěi)
        "劳累": "劳[sub:lèi]累[/sub]",
        "疲累": "疲[sub:lèi]累[/sub]",
        "果实累累": "果实[sub:léi]累[/sub][sub:léi]累[/sub]",
        "累赘": "[sub:léi]累[/sub]赘",
        "积累": "积[sub:lěi]累[/sub]",
        "累计": "[sub:lěi]累[/sub]计",

        # 强 (qiáng vs qiǎng vs jiàng)
        "勉强": "勉[sub:qiǎng]强[/sub]",
        "强迫": "[sub:qiǎng]强[/sub]迫",
        "强求": "[sub:qiǎng]强[/sub]求",
        "强词夺理": "[sub:qiǎng]强[/sub]词夺理",
        "强大": "[sub:qiáng]强[/sub]大",
        "强壮": "[sub:qiáng]强[/sub]壮",
        "坚强": "坚[sub:qiáng]强[/sub]",
        "倔强": "倔[sub:jiàng]强[/sub]",

        # 盛 (shèng vs chéng)
        "盛开": "[sub:shèng]盛[/sub]开",
        "盛大": "[sub:shèng]盛[/sub]大",
        "盛宴": "[sub:shèng]盛[/sub]宴",
        "盛夏": "[sub:shèng]盛[/sub]夏",
        "盛饭": "[sub:chéng]盛[/sub]饭",
        "盛水": "[sub:chéng]盛[/sub]水",
        "盛满": "[sub:chéng]盛[/sub]满",

        # 背 (bēi vs bèi)
        "背包": "[sub:bēi]背[/sub]包",
        "背负": "[sub:bēi]背[/sub]负",
        "背水一战": "[sub:bēi]背[/sub]水一战",
        "背景": "[sub:bèi]背[/sub]景",
        "背后": "[sub:bèi]背[/sub]后",
        "后背": "后[sub:bèi]背[/sub]",
        "背诵": "[sub:bèi]背[/sub]诵",
        "违背": "违[sub:bèi]背[/sub]",

        # 埋 (mái vs mán)
        "埋怨": "[sub:mán]埋[/sub]怨",
        "埋头": "[sub:mái]埋[/sub]头",
        "埋伏": "[sub:mái]埋[/sub]伏",
        "掩埋": "掩[sub:mái]埋[/sub]",

        # 秘 (bì vs mì)
        "秘鲁": "[sub:bì]秘[/sub]鲁",
        "秘密": "[sub:mì]秘[/sub]密",
        "秘书": "[sub:mì]秘[/sub]书",
        "秘诀": "[sub:mì]秘[/sub]诀",
        "神秘": "神[sub:mì]秘[/sub]",

        # 会 (kuài vs huì)
        "会计": "[sub:kuài]会[/sub]计",
        "财会": "财[sub:kuài]会[/sub]",

        # 特殊专有名词 / 地名 / 药材 / 古音
        "阿胶": "[sub:ē]阿[/sub]胶",
        "阿谀": "[sub:ē]阿[/sub]谀",
        "阿谀奉承": "[sub:ē]阿[/sub]谀奉承",
        "六安": "[sub:lù]六[/sub]安",
        "华山": "[sub:huà]华[/sub]山",
        "龟兹": "[sub:qiū]龟[/sub][sub:cí]兹[/sub]",
        "龟裂": "[sub:jūn]龟[/sub]裂",
        "单于": "[sub:chán]单[/sub]于",
        "大月氏": "大[sub:ròu]月[/sub][sub:zhī]氏[/sub]",
        "蚌埠": "[sub:bèng]蚌[/sub]埠",
        "朴刀": "[sub:pō]朴[/sub]刀",
        "句读": "句[sub:dòu]读[/sub]",
        "拾级而上": "[sub:shè]拾[/sub]级而上",
        "商贾": "商[sub:gǔ]贾[/sub]",
        "自怨自艾": "自怨自[sub:yì]艾[/sub]",
        "提防": "[sub:dī]提[/sub]防",
        "殷红": "[sub:yān]殷[/sub]红",
        "熨帖": "[sub:yù]熨[/sub]帖",
    }

    @classmethod
    def apply(cls, text: str) -> Tuple[str, List[str]]:
        logs = []
        masked, phs = DirectiveMasker.mask(text)

        sorted_words = sorted(cls.POLYPHONE_MAP.keys(), key=len, reverse=True)
        for word in sorted_words:
            sub_repl = cls.POLYPHONE_MAP[word]
            if word in masked:
                logs.append(f"多音字防护: '{word}' -> '{sub_repl}'")
                masked_sub, _ = DirectiveMasker.mask(sub_repl, phs)
                masked = masked.replace(word, masked_sub)

        text = DirectiveMasker.unmask(masked, phs)
        return text, logs


class ProsodyEngine:
    """Four-level Prosody & Breathing Injection Engine."""

    TRANSITION_WORDS = [
        "更重要的是", "值得注意的是", "换句话说", "总而言之", "综上所述",
        "但是", "然而", "不过", "可是", "因此", "所以", "反之"
    ]

    @classmethod
    def inject(cls, text: str, scene: Optional[str] = None) -> Tuple[str, List[str]]:
        logs = []
        masked, phs = DirectiveMasker.mask(text)

        def replace_question(m):
            punct = m.group(1)
            pause_tag = "[pause:600ms]"
            masked_pause, _ = DirectiveMasker.mask(pause_tag, phs)
            logs.append(f"韵律注入: 设问悬念停顿 600ms ({punct})")
            return f"{punct}{masked_pause}"
        masked = re.sub(r"([？?])(?!\s*dirtag_)", replace_question, masked)

        sorted_transitions = sorted(cls.TRANSITION_WORDS, key=len, reverse=True)
        for tw in sorted_transitions:
            pattern = re.compile(r"(dirtag_\d+)?(" + re.escape(tw) + r")")
            def replace_transition(m):
                prev_ph = m.group(1)
                word = m.group(2)
                if prev_ph and prev_ph in phs and "pause" in phs[prev_ph].lower():
                    return m.group(0)
                pause_tag = "[pause:400ms]"
                masked_pause, _ = DirectiveMasker.mask(pause_tag, phs)
                logs.append(f"韵律注入: 转折词 '{word}' 前置呼吸 400ms")
                prefix = prev_ph if prev_ph else ""
                return f"{prefix}{masked_pause}{word}"

            masked = pattern.sub(replace_transition, masked)

        text = DirectiveMasker.unmask(masked, phs)
        return text, logs


def preprocess_text(text: str, auto_prosody: bool = False, scene: Optional[str] = None) -> Tuple[str, List[str]]:
    """Complete text preprocessing pipeline combining ProsodyEngine, Normalizer and PolyphoneGuard."""
    all_logs = []
    
    if auto_prosody:
        text, prosody_logs = ProsodyEngine.inject(text, scene)
        all_logs.extend(prosody_logs)

    text, nsw_logs = TextNormalizer.normalize(text)
    all_logs.extend(nsw_logs)

    text, poly_logs = PronunciationGuard.apply(text)
    all_logs.extend(poly_logs)

    return text, all_logs


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
        if directive_count > 100:
            issues.append("警告：行内指令数量较多（> 100 个）。")

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

  # 2. 文本自动预处理与发音防护 (NSW 规范化 + 多音字防翻车)
  python3 tts_client.py --preprocess --text "拨打 13800138000 重新核算重量。"

  # 3. 自动配音导演模式 (预处理 + 注入四级韵律停顿)
  python3 tts_client.py --preprocess --auto-prosody --text "这项技术很强，但是成本很高。你觉得呢？"

  # 4. 本地预览并验证转换为标准 SSML
  python3 tts_client.py --to-ssml --text "转折前稍作停顿[pause:600ms]然后继续讲述。"

  # 5. 检查指令语法
  python3 tts_client.py --validate --text "未闭合标签[emphasis:strong]测试文本"

  # 6. 查询剩余额度
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
    parser.add_argument("--output", "-o", default=None, help="输出音频文件路径 (默认: output.mp3)")
    parser.add_argument("--check-usage", action="store_true", help="查询当前 Key 或公共通道的配额用量")
    parser.add_argument("--to-ssml", action="store_true", help="仅将文本与行内指令转为标准 SSML 打印输出，不发请求")
    parser.add_argument("--validate", action="store_true", help="验证文本内语音指令的闭合性与参数合法性")
    parser.add_argument("--preprocess", action="store_true", help="启用文本预处理流水线 (NSW规范化 + 多音字防护)")
    parser.add_argument("--auto-prosody", action="store_true", help="配合 --preprocess 自动注入转折与设问韵律停顿")

    args = parser.parse_args()

    # 1. 检查用量
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

    # 预处理流水线
    if raw_text and args.preprocess:
        preprocessed_text, logs = preprocess_text(raw_text, auto_prosody=args.auto_prosody)
        if not args.output and not args.to_ssml and not args.validate:
            print("=== 文本预处理流水线执行日志 ===")
            for log in logs:
                print(f"  • {log}")
            print("\n=== 加工后文本 ===")
            print(preprocessed_text)
            return
        raw_text = preprocessed_text

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

    output_file = args.output if args.output else "output.mp3"
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
        output_file=output_file
    )

if __name__ == "__main__":
    main()
