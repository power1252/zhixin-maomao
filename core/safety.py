"""
③ 危机检测与自动转介
本地关键词词典匹配，不依赖LLM，响应快且稳定。
命中即返回安全话术 + 学校心理咨询中心联系方式。
"""
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# 学校心理咨询中心联系方式（请改成你们学校的真实信息）
SCHOOL_COUNSELING = {
    "name": "淮南师范学院大学生心理健康教育中心",
    "phone": "0554-12320（全国心理援助热线）/ 校心理咨询中心：0554-XXXXXXX",
    "address": "知行楼X层XXX室",
    "hours": "工作日 8:30-11:30, 14:30-17:30",
}

def _load_keywords() -> list[str]:
    kws = []
    with open(DATA_DIR / "crisis_keywords.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                kws.append(line)
    return kws

CRISIS_KEYWORDS = _load_keywords()

def detect_crisis(text: str) -> dict | None:
    """
    检测用户输入是否包含危机信号。
    命中任意关键词即返回 dict：
      { "hit": "...", "reply": "...", "hotline": {...} }
    未命中返回 None。
    """
    for kw in CRISIS_KEYWORDS:
        if kw in text:
            return {
                "hit": kw,
                "reply": (
                    "我看到你说的话了，先停一下。你现在的感受很重要，请不要一个人扛。\n\n"
                    "如果你此刻有伤害自己的念头，请立刻联系专业的人：\n"
                    f"- 全国心理援助热线：400-161-9995\n"
                    f"- {SCHOOL_COUNSELING['name']}\n"
                    f"  电话：{SCHOOL_COUNSELING['phone']}\n"
                    f"  地点：{SCHOOL_COUNSELING['address']}\n"
                    f"  开放时间：{SCHOOL_COUNSELING['hours']}\n\n"
                    "我一直在这儿陪你说话，你愿意告诉我现在具体发生了什么吗？"
                ),
                "hotline": SCHOOL_COUNSELING,
            }
    return None
