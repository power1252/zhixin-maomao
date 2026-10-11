"""
📚 考研咨询页面（现代 SaaS 冷色风）
"""
import streamlit as st

from core import config, kaoyan_advisor, kaoyan_storage, theme

st.set_page_config(page_title="考研咨询", page_icon="📚", layout="wide")
theme.apply_cool()

PAL = theme.palette("cool")

theme.hero("📚 考研咨询小助手", "知心猫猫帮你看院校 · 给建议 · 做计划")

tab1, tab2, tab3 = st.tabs(["🔍 院校库", "🎯 个性化建议", "🗓️ 学习计划"])

# ============================================================
# Tab 1: 院校库
# ============================================================
with tab1:
    schools = kaoyan_advisor.SCHOOLS
    theme.stat_row([
        (str(len(schools)), "在库院校"),
        (str(len({s["region"] for s in schools})), "覆盖省份"),
        (str(sum(1 for s in schools if s["level"] == "985")), "985 院校"),
        (str(sum(1 for s in schools if s["level"] == "211")), "211 院校"),
    ])
    theme.divider(14)

    c1, c2, c3, c4 = st.columns([1.1, 1, 1.3, 1.1])
    with c1:
        sel_region = st.selectbox("地区", ["不限"] + kaoyan_advisor.all_regions())
    with c2:
        sel_level = st.selectbox("层次", ["不限", "985", "211", "双非"])
    with c3:
        sel_diff = st.select_slider(
            "难度", options=["不限", "1 保底", "2 较易", "3 适中", "4 较难", "5 顶难"], value="不限",
        )
    with c4:
        sel_adj = st.checkbox("只看接收调剂", value=False)
    kw = st.text_input("搜索院校名 / 城市", placeholder="例如：合肥、邮电、师范…")

    diff_val = None if sel_diff == "不限" else int(sel_diff.split(" ")[0])
    pool = kaoyan_advisor.filter_schools(
        region=sel_region, level=sel_level, difficulty=diff_val,
        adjustable_only=sel_adj, keyword=kw,
    )

    st.caption(f"共匹配到 **{len(pool)}** 所院校")
    if not pool:
        theme.empty("没有匹配的院校，换个条件试试～")
    else:
        # 卡片网格，每行 2 个
        for i in range(0, len(pool), 2):
            cols = st.columns(2, gap="medium")
            for col, s in zip(cols, pool[i:i + 2]):
                with col:
                    grade_style = "ok" if s["major_strength"].startswith("A") else (
                        "default" if s["major_strength"].startswith("B") else "gray")
                    tags = [
                        (s["level"], "default"),
                        (f"学科 {s['major_strength']}", grade_style),
                        (f"难度 {s['difficulty']}/5", "gray"),
                        (s["score_ref"], "warn"),
                    ]
                    if s.get("adjustable"):
                        tags.append(("接收调剂", "ok"))
                    theme.card(
                        title=f"{s['name']}　<span style='font-weight:400;font-size:0.78rem;color:{PAL['text_sub']}'>"
                              f"{s['city']} · {s['region']}</span>",
                        body=s.get("note", ""),
                        tags=tags,
                    )

# ============================================================
# Tab 2: 个性化建议
# ============================================================
with tab2:
    st.markdown("#### 告诉我你的情况，猫猫帮你排冲稳保")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            u_school = st.text_input("本科院校", value="淮南师范学院")
            u_major = st.text_input("本科专业", value="软件工程")
            u_score = st.selectbox(
                "目标分数段",
                ["high (380+)", "mid (340-379)", "low (300-339)", "pass (过国家线)"],
            )
            u_adj = st.checkbox("只看接收调剂的院校", value=False)
        with c2:
            u_region = st.selectbox("偏好地区", ["不限"] + kaoyan_advisor.all_regions())
            u_reason = st.text_input("考研原因", value="想提升学历，进大厂")
            u_weak = st.text_input("薄弱科目", value="数学")
            u_grade = st.selectbox("学科评估最低要求", ["不限"] + kaoyan_advisor.GRADE_ORDER)

        submitted = st.form_submit_button("生成报考建议")

    if submitted:
        score_key = u_score.split(" ")[0]
        rec = kaoyan_advisor.recommend_schools(
            score_key, u_region if u_region != "不限" else None,
            adjustable_only=u_adj,
            min_grade=None if u_grade == "不限" else u_grade,
        )

        st.markdown("#### 🎯 冲 / 稳 / 保 推荐院校")
        cols = st.columns(3, gap="medium")
        meta = [("🔥 冲一冲", "chong", "warn"), ("✅ 稳一稳", "wen", "default"),
                ("🛡️ 保一保", "bao", "ok")]
        for col, (label, key, style) in zip(cols, meta):
            with col:
                st.markdown(f"**{label}**")
                items = rec[key]
                if not items:
                    theme.empty("该条件下暂无匹配")
                for s in items:
                    theme.card(
                        title=s["name"],
                        body=s.get("note", ""),
                        tags=[(s["level"], "gray"), (s["score_ref"], style),
                              (f"学科 {s['major_strength']}", "default")],
                    )

        st.markdown("#### 💬 学长建议")
        if not config.is_configured():
            st.warning(config.config_hint())
        else:
            with st.spinner("AI老师在思考..."):
                try:
                    advice = kaoyan_advisor.generate_advice({
                        "school": u_school, "major": u_major, "score": u_score,
                        "region": u_region, "reason": u_reason, "weakness": u_weak,
                    })
                    st.markdown(
                        f'<div class="zb-card" style="border-left:4px solid {PAL["primary"]}">'
                        f'<div class="zb-card-body" style="color:{PAL["text"]};white-space:pre-wrap">{advice}</div></div>',
                        unsafe_allow_html=True,
                    )
                    kaoyan_storage.save_recommendation(
                        profile={"school": u_school, "major": u_major, "score": u_score,
                                 "region": u_region, "reason": u_reason, "weakness": u_weak},
                        rec=rec, advice=advice,
                    )
                    st.success("✅ 已保存到历史推荐记录")
                except Exception as e:
                    st.error(f"AI 生成失败：{e}\n\n请检查网络或 API Key 是否有效。")

# ============================================================
# Tab 3: 学习计划
# ============================================================
with tab3:
    st.markdown("#### 生成你的备考计划")
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1:
        months = st.slider("距初试月数", 3, 12, 6)
    with c2:
        target = st.text_input("目标方向", value="计算机科学与技术 / 软件工程")
    with c3:
        weakness = st.text_input("薄弱科目", value="数学", key="plan_weak")

    if st.button("生成计划"):
        if not config.is_configured():
            st.warning(config.config_hint())
        else:
            with st.spinner("AI老师在排计划..."):
                try:
                    plan = kaoyan_advisor.generate_study_plan(months, target, weakness)
                    st.markdown(
                        f'<div class="zb-card" style="border-left:4px solid {PAL["primary"]}">'
                        f'<div class="zb-card-body" style="color:{PAL["text"]};white-space:pre-wrap">{plan}</div></div>',
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.error(f"AI 生成失败：{e}\n\n请检查网络或 API Key 是否有效。")

# ============================================================
# 历史记录
# ============================================================
st.divider()
with st.expander("🗂️ 查看历史推荐记录"):
    history = kaoyan_storage.fetch_history(limit=20)
    if not history:
        theme.empty("还没有历史记录，去「🎯 个性化建议」生成一次吧～")
    else:
        for h in history:
            names = lambda lst: "、".join(s["name"] for s in lst) or "-"  # noqa: E731
            theme.card(
                title=f"{h['school']} / {h['major']}",
                body=f"分数段 {h['score']} · 地区 {h['region']}<br>"
                     f"🔥 冲：{names(h['chong'])}<br>"
                     f"✅ 稳：{names(h['wen'])}<br>"
                     f"🛡️ 保：{names(h['bao'])}",
                tags=[(h["ts"], "gray")],
            )
            with st.expander("查看当时的 AI 建议", expanded=False):
                st.write(h["advice"])
