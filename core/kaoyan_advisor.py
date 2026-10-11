"""
考研咨询模块
- 院校数据库匹配（冲/稳/保三档）
- 按分数段/学科等级/调剂友好度筛选
- 调用LLM生成个性化报考建议
- 调用LLM生成学习计划

数据字段（data/schools.json）：
  name 院校名 / level 层次 / region 省份 / city 城市
  major_strength 学科评估等级 / difficulty 难度1-5
  score_ref 参考分数 / adjustable 是否接收调剂 / note 备注
"""
import json
from pathlib import Path

from openai import OpenAI

from . import config

DATA_DIR = Path(__file__).parent.parent / "data"


def _get_client() -> OpenAI:
    """惰性创建客户端。未配置 Key 时抛出可读异常，由页面捕获。"""
    if not config.is_configured():
        raise RuntimeError(config.config_hint())
    return OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


def _load_schools() -> list[dict]:
    with open(DATA_DIR / "schools.json", encoding="utf-8") as f:
        return json.load(f)


SCHOOLS = _load_schools()

# 分数段 → 冲/稳/保对应难度
SCORE_LEVELS = {
    "high": {"label": "高分冲刺型 (380+)", "diff": {"chong": 5, "wen": 4, "bao": 3}},
    "mid":  {"label": "中等水平型 (340-379)", "diff": {"chong": 4, "wen": 3, "bao": 2}},
    "low":  {"label": "稳步提升型 (300-339)", "diff": {"chong": 3, "wen": 2, "bao": 1}},
    "pass": {"label": "过线求稳型 (过国家线)", "diff": {"chong": 2, "wen": 1, "bao": 1}},
}

# 学科评估等级排序（用于筛选）
GRADE_ORDER = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C"]


def _match(diff: int, region_pref: str | None, adjustable_only: bool,
           min_grade: str | None, limit: int = 3) -> list[dict]:
    """按难度 + 地区 + 调剂 + 学科等级筛选院校。"""
    pool = [s for s in SCHOOLS if s.get("difficulty") == diff]

    if region_pref and region_pref != "不限":
        pool = [s for s in pool if s.get("region") == region_pref or s.get("city") == region_pref]

    if adjustable_only:
        pool = [s for s in pool if s.get("adjustable")]

    if min_grade and min_grade in GRADE_ORDER:
        cutoff = GRADE_ORDER.index(min_grade)
        pool = [s for s in pool if s.get("major_strength") in GRADE_ORDER
                and GRADE_ORDER.index(s["major_strength"]) <= cutoff]

    # 学科等级高者优先
    pool.sort(key=lambda s: GRADE_ORDER.index(s["major_strength"])
              if s.get("major_strength") in GRADE_ORDER else 99)
    return pool[:limit]


def recommend_schools(score_level: str, region_pref: str | None = None,
                      adjustable_only: bool = False,
                      min_grade: str | None = None,
                      limit: int = 3) -> dict:
    """
    根据用户自评分数段，给出冲/稳/保三档院校。
    score_level: "high"(380+) / "mid"(340-379) / "low"(300-339) / "pass"(过国家线)
    """
    cfg = SCORE_LEVELS.get(score_level, SCORE_LEVELS["mid"])
    diff = cfg["diff"]

    return {
        "chong": _match(diff["chong"], region_pref, adjustable_only, min_grade, limit),
        "wen":   _match(diff["wen"],   region_pref, adjustable_only, min_grade, limit),
        "bao":   _match(diff["bao"],   region_pref, adjustable_only, min_grade, limit),
    }


def filter_schools(region: str = "不限", level: str = "不限",
                   difficulty: int | None = None,
                   adjustable_only: bool = False,
                   keyword: str = "") -> list[dict]:
    """通用筛选，供院校查询 Tab 使用。"""
    pool = SCHOOLS
    if region != "不限":
        pool = [s for s in pool if s.get("region") == region or s.get("city") == region]
    if level != "不限":
        pool = [s for s in pool if s.get("level") == level]
    if difficulty is not None:
        pool = [s for s in pool if s.get("difficulty") == difficulty]
    if adjustable_only:
        pool = [s for s in pool if s.get("adjustable")]
    if keyword.strip():
        kw = keyword.strip()
        pool = [s for s in pool if kw in s.get("name", "") or kw in s.get("city", "")]
    return pool


def all_regions() -> list[str]:
    return sorted({s["region"] for s in SCHOOLS})


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

    resp = _get_client().chat.completions.create(
        model=config.MODEL,
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

    resp = _get_client().chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1200,
    )
    return resp.choices[0].message.content
