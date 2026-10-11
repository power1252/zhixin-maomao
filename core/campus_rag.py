"""
④ 校园场景RAG（轻量版，不装向量库）
本地 JSON 语料 + 关键词匹配，命中后把对应回复作为"参考话术"塞给LLM。
大二学生可直接跑，不需要部署 embedding 模型。

优化点：
  - 支持多话题命中（按得分排序取前 N），而不是只取一个。
  - 得分做长度加权，避免"钱""累"这类短词压过更有信息量的长词。
  - 语料可热重载（改完 JSON 不用重启）。
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
FAQ_PATH = DATA_DIR / "campus_faq.json"


def _load_faq() -> list[dict]:
    with open(FAQ_PATH, encoding="utf-8") as f:
        return json.load(f)


FAQ = _load_faq()


def _score(item: dict, text: str) -> int:
    """计算某话题与用户输入的匹配得分。长关键词权重更高。"""
    total = 0
    for kw in item["keywords"]:
        if kw in text:
            # 长度加权：2字词计1分，4字词计3分（len-1）
            total += max(1, len(kw) - 1)
    return total


def retrieve_campus_context(user_text: str, top_n: int = 2) -> str:
    """
    根据用户输入，匹配最相关的校园场景，返回一段提示给LLM。
    没命中返回空字符串。
    """
    scored = []
    for item in FAQ:
        s = _score(item, user_text)
        if s > 0:
            scored.append((s, item))

    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_n]

    blocks = []
    for _, item in top:
        blocks.append(f"「{item['topic']}」话题，可参考口吻（不要照抄）：{item['reply']}")

    topics = "、".join(i["topic"] for _, i in top)
    return (
        f"[校园场景参考] 用户可能属于以下话题：{topics}。\n"
        + "\n".join(blocks)
        + "\n请结合对话上下文自然表达，不要直接复用上面的句子。"
    )


def reload_faq():
    """热重载语料（改动 campus_faq.json 后可调用）。"""
    global FAQ
    FAQ = _load_faq()
