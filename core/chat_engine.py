"""
对话引擎：串起 ②③④⑤ 四个研究方向。
流程：
  1) ③ 危机检测 —— 命中直接返回安全话术，不调LLM
  2) ⑤ 读长期记忆 —— 拉最近10轮历史
  3) ④ 校园RAG —— 命中场景就把参考话术塞prompt
  4) 调LLM（DeepSeek / OpenAI兼容接口）
  5) ② 解析情绪标签 → 存SQLite
  6) ⑤ 把这轮对话写入记忆
"""
import os
import re
from openai import OpenAI

from .system_prompt import SYSTEM_PROMPT
from . import safety, emotion_tracker, campus_rag, memory

# ===== 配置：优先从 Streamlit Secrets / 环境变量读 =====
# 本地开发：直接写在下面这行
# 云端部署：在 Streamlit Secrets 里配 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
try:
    import streamlit as st
    API_KEY = st.secrets.get("LLM_API_KEY", os.getenv("LLM_API_KEY", "sk-1b253798a2864e188ba3d3794373c3e2"))
    BASE_URL = st.secrets.get("LLM_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.deepseek.com"))
    MODEL = st.secrets.get("LLM_MODEL", os.getenv("LLM_MODEL", "deepseek-chat"))
except ImportError:
    API_KEY = os.getenv("LLM_API_KEY", "sk-1b253798a2864e188ba3d3794373c3e2")
    BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

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
    # ③ 危机检测（最高优先级）
    crisis = safety.detect_crisis(user_text)
    if crisis:
        emotion_tracker.log_mood("sadness", user_text, crisis["reply"])
        memory.add_message("user", user_text)
        memory.add_message("assistant", crisis["reply"])
        return crisis["reply"]

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

    # 调LLM
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.85,
        max_tokens=300,
    )
    raw = resp.choices[0].message.content
    emotion, reply = _parse_reply(raw)

    # ② 落库心情
    emotion_tracker.log_mood(emotion, user_text, reply)
    # ⑤ 写入记忆
    memory.add_message("user", user_text)
    memory.add_message("assistant", reply)

    return reply
