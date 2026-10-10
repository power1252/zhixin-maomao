"""
知心猫猫 —— Streamlit 主入口
启动：streamlit run app.py
"""
from pathlib import Path

import streamlit as st

from core import chat_engine, memory, safety

ASSETS = Path(__file__).parent / "assets"
CAT_AVATAR = str(ASSETS / "cat_avatar.png")

st.set_page_config(page_title="知心猫猫", page_icon="🐱", layout="centered")

# 顶部品牌区：猫咪头像 + 标题
col1, col2 = st.columns([1, 4])
with col1:
    st.image(CAT_AVATAR, width=110)
with col2:
    st.title("🐱 知心猫猫")
    st.caption("一只橘色小猫娘 · 7×24小时陪你唠嗑 · 把尾巴借给你撸")

# 侧边栏
with st.sidebar:
    st.image(CAT_AVATAR, width=80)
    st.header("设置")
    if st.button("🗑️ 清空对话记忆"):
        memory.clear_history()
        st.session_state.messages = []
        st.success("已清空，猫猫不记得啦~")
    st.divider()
    st.info(
        "本助手不是专业心理咨询喵。\n"
        "如有自伤念头，请立即联系：\n"
        "400-161-9995（全国心理援助）"
    )

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "喵~ 我是知心猫猫，蜷在你桌边的那只橘猫。今天过得怎么样？尾巴借给你撸。"}
    ]

# 渲染历史（assistant用猫咪头像）
for msg in st.session_state.messages:
    avatar = CAT_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 用户输入
user_input = st.chat_input("和猫猫说说...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant", avatar=CAT_AVATAR):
        with st.spinner("猫猫在听，尾巴竖起来了..."):
            reply = chat_engine.chat(user_input)
            st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
