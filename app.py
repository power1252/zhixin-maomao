"""
知心猫猫 —— Streamlit 主入口（治愈暖色风）
启动：streamlit run app.py
"""
from datetime import datetime
from pathlib import Path

import streamlit as st

from core import chat_engine, config, memory, safety, theme

ASSETS = Path(__file__).parent / "assets"
CAT_AVATAR = str(ASSETS / "cat_avatar.png")

st.set_page_config(page_title="知心猫猫", page_icon="🐱", layout="centered")

# ===== 注入治愈暖色主题 =====
theme.apply_warm()

# ===== 顶部 Hero =====
theme.hero(
    "🐱 知心猫猫",
    "蜷在你桌边的那只橘猫 · 7×24 小时陪你唠嗑 · 把尾巴借给你撸",
)

# ===== 侧边栏 =====
with st.sidebar:
    st.image(CAT_AVATAR, width=76)
    st.markdown("### 设置")

    # 配置状态
    if config.is_configured():
        st.success("🔌 大模型已连接")
    else:
        st.error("🔌 未配置大模型 Key")
        st.caption("猫猫现在只能做危机检测和本地应答。")

    # 记忆条数
    _mem_count = len(memory.recent_messages(limit=999))
    st.caption(f"🧠 当前记得 {_mem_count} 条对话")

    if st.button("🗑️ 清空对话记忆", use_container_width=True):
        memory.clear_history()
        st.session_state.messages = []
        st.success("已清空，猫猫不记得啦~")
    st.divider()

    st.markdown("##### 🆘 需要即时帮助？")
    st.info(
        "本助手不是专业心理咨询喵。\n\n"
        "如有自伤念头，请立即联系：\n"
        "**400-161-9995**（全国心理援助热线，24h）"
    )
    st.caption("另外三个页面在左上角导航栏 →")

# ===== 未配置 Key 提示 =====
if not config.is_configured():
    st.warning(config.config_hint())

# ===== 开场引导（仅首轮显示）=====
STARTERS = [
    ("😔 最近考试砸了", "最近考试砸了，感觉自己好没用"),
    ("😰 期末好焦虑", "期末快到了，好多东西没复习，好焦虑"),
    ("🛏️ 宿舍关系很累", "和室友相处好累，不知道怎么办"),
    ("🧭 不知道以后干嘛", "快毕业了，不知道自己该做什么"),
]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "喵~ 我是知心猫猫，蜷在你桌边的那只橘猫。今天过得怎么样？尾巴借给你撸。",
        }
    ]

# 注意：这里必须在处理输入**之前**读取待处理输入，
# 否则引导按钮点击后 _pending_input 已被消费，判断会滞后一轮。
_pending_pre = st.session_state.get("_pending_input")

# 首轮判定：还没有任何用户消息，且本次也没有待处理输入
_is_first_turn = not any(m["role"] == "user" for m in st.session_state.messages) \
    and not _pending_pre

if _is_first_turn:
    st.caption("不知道从哪说起？点一个试试：")
    cols = st.columns(2)
    for i, (label, text) in enumerate(STARTERS):
        with cols[i % 2]:
            if st.button(label, key=f"starter_{i}", use_container_width=True):
                st.session_state["_pending_input"] = text
                st.rerun()

# ===== 渲染历史消息 =====
for msg in st.session_state.messages:
    avatar = CAT_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# ===== 输入处理 =====
_pending = st.session_state.pop("_pending_input", None)
user_input = st.chat_input("和猫猫说说...") or _pending

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant", avatar=CAT_AVATAR):
        with st.spinner("猫猫在听，尾巴竖起来了..."):
            reply = chat_engine.chat(user_input)
            st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ===== 最后一轮的重生成按钮 =====
if len(st.session_state.messages) >= 3:
    if st.button("🔄 换一种说法", key="regen_last"):
        last_user = next(
            (m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"),
            None,
        )
        if last_user:
            st.session_state.messages.pop()   # 去掉刚才的 AI 回复
            with st.spinner("猫猫换个说法..."):
                reply2 = chat_engine.chat(last_user)
            st.session_state.messages.append({"role": "assistant", "content": reply2})
            st.rerun()

