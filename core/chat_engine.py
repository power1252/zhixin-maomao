"""
对话引擎：串起 ②③④⑤ 四个研究方向。
流程：
  1) ③ 危机检测 —— 命中直接返回安全话术，不调LLM
  2) ⑤ 读长期记忆 —— 拉最近10轮历史
  3) ④ 校园RAG —— 命中场景就把参考话术塞prompt
  4) 调LLM（DeepSeek / OpenAI兼容接口）
  5) ② 解析情绪标签 → 存SQLite
  6) ⑤ 把这轮对话写入记忆

健壮性说明：
  - 未配置 API Key 时不会在 import 阶段崩溃，而是返回友好提示。
  - LLM 调用超时/报错时不会把堆栈抛给用户，返回可读的兜底话术。
"""
import re

from openai import OpenAI

from . import campus_rag, config, emotion_tracker, memory, safety
from .system_prompt import SYSTEM_PROMPT

# ===== 客户端按需惰性创建（避免无 Key 时 import 崩溃）=====
_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    """惰性创建 OpenAI 客户端。未配置 Key 时返回 None。"""
    global _client
    if _client is None and config.is_configured():
        _client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
    return _client


# 模块级 client，供 kaoyan_advisor / cs408_advisor 复用
# 注意：它可能是 None，调用方需先判断 config.is_configured()
client = _get_client()

# LLM 调用失败时的兜底回复
_FALLBACK_REPLY = "喵…我刚刚走神了一下，没听清。你再说一遍好不好？"


def _parse_reply(text: str) -> tuple[str, str]:
    """
    解析LLM输出：
      EMOTION: anxiety
      REPLY: 我懂...
    返回 (emotion, reply)。解析失败默认 calm。
    """
    m = re.search(r"EMOTION:\s*(\w+)", text)
    emotion = m.group(1) if m else "calm"
    m2 = re.search(r"REPLY:\s*(.+)", text, re.DOTALL)
    reply = m2.group(1).strip() if m2 else text.strip()
    return emotion, reply


def chat(user_text: str) -> str:
    # ③ 危机检测（最高优先级，不依赖 LLM）
    crisis = safety.detect_crisis(user_text)
    if crisis:
        emotion_tracker.log_mood("sadness", user_text, crisis["reply"])
        memory.add_message("user", user_text)
        memory.add_message("assistant", crisis["reply"])
        return crisis["reply"]

    # 未配置 Key：给出明确指引，不抛异常
    if not config.is_configured():
        return config.config_hint()

    # ⑤ 拉长期记忆
    history = memory.recent_messages(limit=10)

    # ④ 校园RAG
    rag_ctx = campus_rag.retrieve_campus_context(user_text)
    system = SYSTEM_PROMPT
    if rag_ctx:
        system += "\n\n" + rag_ctx

    # 组装消息
    messages = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    # 调LLM（失败不崩溃）
    try:
        resp = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            temperature=0.85,
            max_tokens=300,
        )
        raw = resp.choices[0].message.content or ""
        emotion, reply = _parse_reply(raw)
    except Exception:
        return _FALLBACK_REPLY

    # ② 落库心情
    emotion_tracker.log_mood(emotion, user_text, reply)
    # ⑤ 写入记忆
    memory.add_message("user", user_text)
    memory.add_message("assistant", reply)

    return reply
