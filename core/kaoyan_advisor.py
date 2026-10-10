"""
考研咨询模块
- 院校数据库匹配（冲/稳/保三档）
- 调用LLM生成个性化报考建议
- 调用LLM生成学习计划
"""
import json
from pathlib import Path

from openai import OpenAI

from .chat_engine import client, MODEL

DATA_DIR = Path(__file__).parent.parent / "data"

def _load_schools() -> list[dict]:
    with open(DATA_DIR / "schools.json", encoding="utf-8") as f:
        return json.load(f)

SCHOOLS = _load_schools()

def recommend_schools(score_level: str, region_pref: str | None = None) -> dict:
    """
    根据用户自评分数段，给出冲/稳/保三档院校。
    score_level: "high"(380+) / "mid"(340-379) / "low"(300-339) / "pass"(过国家线)
    """
    score_to_difficulty = {
        "high": {"chong": 5, "wen": 4, "bao": 3},
        "mid":  {"chong": 4, "wen": 3, "bao": 2},
        "low":  {"chong": 3, "wen": 2, "bao": 1},
        "pass": {"chong": 2, "wen": 1, "bao": 1},
    }
    diff = score_to_difficulty.get(score_level, score_to_difficulty["mid"])

    def _match(d: int):
        pool = [s for s in SCHOOLS if s["difficulty"] == d]
        if region_pref and region_pref != "不限":
            pool = [s for s in pool if region_pref in s["region"]]
        return pool[:3]

    return {
        "chong": _match(diff["chong"]),
        "wen":   _match(diff["wen"]),
        "bao":   _match(diff["bao"]),
    }

def generate_advice(profile: dict) -> str:
    """
    调用LLM生成个性化报考建议。
    profile: {
        "school": "本科院校", "major": "本科专业", "score": "目标分数",
        "region": "偏好地区", "reason": "考研原因", "weakness": "薄弱科目"
    }
    """
    prompt = f"""你是一位有10年经验的考研辅导老师。请根据以下学生情况，给出报考建议：

【学生情况】
- 本科：{profile.get("school", "未知")}
- 专业：{profile.get("major", "软件工程")}
- 目标分数段：{profile.get("score", "未知")}
- 偏好地区：{profile.get("region", "不限")}
- 考研原因：{profile.get("reason", "未知")}
- 薄弱科目：{profile.get("weakness", "未知")}

【请输出】
1. 推荐定位（冲/稳/保各1个理由）
2. 选校建议（结合他的水平和地区偏好）
3. 风险点提醒
4. 一句话鼓励

语气像学长/学姐，不要端着。"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    return resp.choices[0].message.content

def generate_study_plan(months: int, target: str, weakness: str) -> str:
    """生成学习计划。"""
    prompt = f"""你是考研辅导老师。请给一个准备考{target}方向的学生，做一份{months}个月的备考计划。
他的薄弱科目是：{weakness}。

请按月列出：
- 数学/英语/政治/专业课 四科分别的任务
- 每月重点
- 关键时间节点（报名、预报名、初试）

用表格或分点列出，要具体可执行，不要鸡汤。"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1200,
    )
    return resp.choices[0].message.content
