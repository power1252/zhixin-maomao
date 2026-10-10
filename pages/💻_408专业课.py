"""
💻 408专业课学习助手
"""
import streamlit as st

from core import cs408_advisor

st.set_page_config(page_title="408专业课", page_icon="💻")

# ===== 冷色专业风 CSS =====
st.markdown("""
<style>
    .stApp { background: #F5F7FA !important; }
    h1 { color: #2C5282 !important; font-weight: 700; }
    h2, h3 { color: #2A4365 !important; }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600; color: #4A5568;
    }
    .stButton > button {
        background: #2C5282; color: white; border-radius: 6px;
    }
    .stExpander {
        border-left: 3px solid #2C5282; background: white;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💻 408专业课学习助手")
st.caption("数据结构 · 计组 · 操作系统 · 数据库")

tab1, tab2, tab3 = st.tabs(["📚 知识框架", "📝 经典例题", "🤖 AI讲题"])

# ===== Tab1: 知识框架 =====
with tab1:
    st.subheader("四科知识地图")
    for subj, points in cs408_advisor.KNOWLEDGE_MAP.items():
        with st.expander(f"📖 {subj}"):
            for p in points:
                st.write(f"- {p}")

# ===== Tab2: 经典例题 =====
with tab2:
    st.subheader("经典例题（点击展开详细解析）")
    subj_filter = st.selectbox("筛选科目", ["全部"] + cs408_advisor.SUBJECTS)
    pool = cs408_advisor.QUESTIONS
    if subj_filter != "全部":
        pool = [q for q in pool if q["subject"] == subj_filter]

    for i, q in enumerate(pool):
        with st.expander(f"[{q['subject']}·{q['topic']}] {q['question']}"):
            st.markdown(f"**答案**：{q['answer']}")
            st.markdown(f"**解析**：{q['analysis']}")
            if q.get("correction"):
                st.warning(q["correction"])

# ===== Tab3: AI讲题 =====
with tab3:
    st.subheader("贴一道题，让AI老师给你讲明白")
    subject = st.selectbox("科目", cs408_advisor.SUBJECTS)
    q_text = st.text_area("把题目贴在这里（可以是拍照转文字、或直接打字）", height=150,
                          placeholder="例如：已知某分页系统，页面大小4KB，逻辑地址32位...")
    if st.button("开始讲解") and q_text.strip():
        with st.spinner("AI老师在写板书..."):
            result = cs408_advisor.explain_question(q_text, subject)
            st.write(result)
    st.info("💡 近十年真题可以在王道论坛、考研帮找到PDF，把题目文字粘进来就能讲。")
