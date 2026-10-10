"""
④ 校园场景RAG（轻量版，不装向量库）
本地 JSON 语料 + 关键词匹配，命中后把对应回复作为"参考话术"塞给LLM。
大二学生可直接跑，不需要部署 embedding 模型。
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _load_faq() -> list[dict]:
    with open(DATA_DIR / "campus_faq.json", encoding="utf-8") as f:
        return json.load(f)

FAQ = _load_faq()

def retrieve_campus_context(user_text: str) -> str:
    """
    根据用户输入，匹配最相关的校园场景，返回一段提示给LLM。
    没命中返回空字符串。
    """
    hit_score: dict[str, int] = {}
    for item in FAQ:
        score = sum(1 for kw in item["keywords"] if kw in user_text)
        if score > 0:
            hit_score[item["topic"]] = score

    if not hit_score:
        return ""

    top_topic = max(hit_score, key=hit_score.get)
    top_item = next(i for i in FAQ if i["topic"] == top_topic)
    return (
        f"[校园场景参考] 用户可能属于「{top_topic}」话题。"
        f"可参考以下口吻回应，但不要照抄，要根据对话上下文自然表达：\n"
        f"「{top_item['reply']}」"
    )
