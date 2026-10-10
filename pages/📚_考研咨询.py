"""
📚 考研咨询页面
"""
import streamlit as st

from core import kaoyan_advisor, kaoyan_storage

st.set_page_config(page_title="考研咨询", page_icon="📚")

# ===== 冷色专业风 CSS =====
st.markdown("""
<style>
    .stApp { background: #F5F7FA !important; }
    h1 { color: #2C5282 !important; font-weight: 700; }
    h2, h3 { color: #2A4365 !important; }
    .stButton > button {
        background: #2C5282; color: white; border-radius: 6px;
    }
    .stExpander {
        border-left: 3px solid #2C5282; background: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 考研咨询小助手")
st.caption("知心猫猫帮你看院校 + 给建议 + 做计划")

tab1, tab2, tab3 = st.tabs(["① 院校情况查询", "② 个性化报考建议", "③ 学习计划"])

# ===== Tab 1: 院校查询 =====
with tab1:
    st.subheader("计算机/软件工程考研院校库")
    st.write(f"共收录 {len(kaoyan_advisor.SCHOOLS)} 所代表性院校（可自行扩充 `data/schools.json`）")

    col1, col2 = st.columns(2)
    with col1:
        region = st.selectbox("地区", ["不限"] + sorted({s["region"] for s in kaoyan_advisor.SCHOOLS}))
    with col2:
        level = st.selectbox("学校层次", ["不限", "985", "211", "双非"])

    pool = kaoyan_advisor.SCHOOLS
    if region != "不限":
        pool = [s for s in pool if s["region"] == region]
    if level != "不限":
        pool = [s for s in pool if s["level"] == level]

    st.dataframe(pool, use_container_width=True, hide_index=True)

# ===== Tab 2: 个性化建议 =====
with tab2:
    st.subheader("告诉我你的情况")
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            u_school = st.text_input("本科院校", value="淮南师范学院")
            u_major = st.text_input("本科专业", value="软件工程")
            u_score = st.selectbox("目标分数段", ["high (380+)", "mid (340-379)", "low (300-339)", "pass (过国家线)"])
        with c2:
            u_region = st.selectbox("偏好地区", ["不限", "安徽", "北京", "上海", "江苏", "浙江", "湖北", "陕西", "黑龙江"])
            u_reason = st.text_input("考研原因", value="想提升学历，进大厂")
            u_weak = st.text_input("薄弱科目", value="数学")
        submitted = st.form_submit_button("生成报考建议")

    if submitted:
        score_key = u_score.split(" ")[0]
        rec = kaoyan_advisor.recommend_schools(score_key, u_region if u_region != "不限" else None)

        st.write("### 🎯 冲/稳/保推荐院校")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown("**🔥 冲一冲**")
            for s in rec["chong"]:
                st.write(f"- {s['name']}（{s['level']}，{s['note']}）")
        with cc2:
            st.markdown("**✅ 稳一稳**")
            for s in rec["wen"]:
                st.write(f"- {s['name']}（{s['level']}，{s['note']}）")
        with cc3:
            st.markdown("**🛡️ 保一保**")
            for s in rec["bao"]:
                st.write(f"- {s['name']}（{s['level']}，{s['note']}）")

        st.write("### 💬 学长建议")
        with st.spinner("AI老师在思考..."):
            advice = kaoyan_advisor.generate_advice({
                "school": u_school, "major": u_major, "score": u_score,
                "region": u_region, "reason": u_reason, "weakness": u_weak,
            })
            st.write(advice)
            # 落库
            kaoyan_storage.save_recommendation(
                profile={"school": u_school, "major": u_major, "score": u_score,
                         "region": u_region, "reason": u_reason, "weakness": u_weak},
                rec=rec, advice=advice,
            )
            st.success("✅ 已保存到历史推荐记录")

# ===== Tab 3: 学习计划 =====
with tab3:
    st.subheader("生成你的备考计划")
    months = st.slider("距离初试还有几个月", 3, 12, 6)
    target = st.text_input("目标方向", value="计算机科学与技术 / 软件工程")
    weakness = st.text_input("薄弱科目", value="数学")
    if st.button("生成计划"):
        with st.spinner("AI老师在排计划..."):
            plan = kaoyan_advisor.generate_study_plan(months, target, weakness)
            st.write(plan)

# ===== 历史推荐记录 =====
st.divider()
with st.expander("🗂️ 查看历史推荐记录"):
    history = kaoyan_storage.fetch_history(limit=20)
    if not history:
        st.info("还没有历史记录，去 ② 生成一次报考建议吧。")
    else:
        for h in history:
            with st.container(border=True):
                st.markdown(f"**{h['ts']}** · {h['school']} / {h['major']} · 分数段 {h['score']} · 地区 {h['region']}")
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.caption("🔥 冲")
                    st.write("、".join(s["name"] for s in h["chong"]) or "-")
                with cc2:
                    st.caption("✅ 稳")
                    st.write("、".join(s["name"] for s in h["wen"]) or "-")
                with cc3:
                    st.caption("🛡️ 保")
                    st.write("、".join(s["name"] for s in h["bao"]) or "-")
                with st.expander("查看当时的AI建议"):
                    st.write(h["advice"])
