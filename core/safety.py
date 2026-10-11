"""
③ 危机检测与自动转介
本地关键词词典匹配，不依赖LLM，响应快且稳定。
命中即返回安全话术 + 求助资源。

⚠️ 重要：请把下面 SCHOOL_COUNSELING 换成你所在学校的真实信息。
   若暂时拿不到校级信息，把 phone/address 留空即可——
   系统会自动只展示国家级/省级热线，不会展示假号码误导用户。
"""
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ===== 通用求助资源（真实可拨号，任何时候都展示）=====
HOTLINES = [
    ("全国24小时心理援助热线", "400-161-9995"),
    ("北京心理危机研究与干预中心", "010-82951332"),
    ("教育部华中师范大学心理援助热线", "400-967-8920"),
    ("希望24热线（生命危机干预）", "400-161-9995"),
]

# ===== 学校心理咨询中心（⚠️ 请替换为真实信息）=====
# 拿不到真实信息时保持为空字符串，系统会自动跳过这几行。
SCHOOL_COUNSELING = {
    "name": "",        # 例："淮南师范学院大学生心理健康教育中心"
    "phone": "",       # 例："0554-6861234"
    "address": "",     # 例："知行楼3层305室"
    "hours": "",       # 例："工作日 8:30-11:30, 14:30-17:30"
}


def _has_school_info() -> bool:
    """学校信息是否已配置（至少有名称和电话）。"""
    return bool(SCHOOL_COUNSELING["name"] and SCHOOL_COUNSELING["phone"])


def _load_keywords() -> list[str]:
    kws = []
    with open(DATA_DIR / "crisis_keywords.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                kws.append(line)
    return kws


CRISIS_KEYWORDS = _load_keywords()


def _build_reply() -> str:
    """组装安全话术。学校信息缺失时自动降级为只展示通用热线。"""
    lines = [
        "我看到你说的话了，先停一下。你现在的感受很重要，请不要一个人扛。",
        "",
        "如果你此刻有伤害自己的念头，请立刻联系专业的人：",
        "",
    ]
    for name, phone in HOTLINES:
        lines.append(f"- {name}：{phone}")

    if _has_school_info():
        lines += [
            "",
            f"- {SCHOOL_COUNSELING['name']}",
        ]
        if SCHOOL_COUNSELING["phone"]:
            lines.append(f"  电话：{SCHOOL_COUNSELING['phone']}")
        if SCHOOL_COUNSELING["address"]:
            lines.append(f"  地点：{SCHOOL_COUNSELING['address']}")
        if SCHOOL_COUNSELING["hours"]:
            lines.append(f"  开放时间：{SCHOOL_COUNSELING['hours']}")

    lines += [
        "",
        "如果身边有人，试着告诉 TA 你现在的状态；如果没人，打上面的电话，随时都有人接。",
        "我一直在这儿陪你说话，你愿意告诉我现在具体发生了什么吗？",
    ]
    return "\n".join(lines)


# 启动时组装一次（关键词命中后直接返回，保证毫秒级响应）
_CRISIS_REPLY = _build_reply()


def detect_crisis(text: str) -> dict | None:
    """
    检测用户输入是否包含危机信号。
    命中任意关键词即返回 dict：
      { "hit": "...", "reply": "...", "hotlines": [...] }
    未命中返回 None。
    """
    for kw in CRISIS_KEYWORDS:
        if kw in text:
            return {
                "hit": kw,
                "reply": _CRISIS_REPLY,
                "hotlines": [{"name": n, "phone": p} for n, p in HOTLINES],
                "school": SCHOOL_COUNSELING if _has_school_info() else None,
            }
    return None


def reload_keywords():
    """热重载关键词词典（改动 crisis_keywords.txt 后可调用）。"""
    global CRISIS_KEYWORDS
    CRISIS_KEYWORDS = _load_keywords()
