"""
💻 408专业课学习助手（现代 SaaS 冷色风）
Tab：知识框架 / 经典例题 / AI讲题 / 错题本
"""
import streamlit as st

from core import config, cs408_advisor, theme, wrongbook

st.set_page_config(page_title="408专业课", page_icon="💻", layout="wide")
theme.apply_cool()

PAL = theme.palette("cool")

theme.hero("💻 408 专业课学习助手", "数据结构 · 计算机组成原理 · 操作系统 · 数据库")

# ===== 顶部统计 =====
_s = wrongbook.stats()
theme.stat_row([
    ("4", "覆盖科目"),
    (str(len(cs408_advisor.QUESTIONS)), "经典例题"),
    (str(_s["total"]), "错题本总数"),
    (str(_s["unmastered"]), "待攻克"),
])
theme.divider(14)

tab1, tab2, tab3, tab4 = st.tabs(["📚 知识框架", "📝 经典例题", "🤖 AI讲题", "📕 错题本"])

# ============================================================
# Tab1: 知识框架
# ============================================================
with tab1:
    st.markdown("#### 四科知识地图")
    st.caption("点击卡片展开各科考点清单")

    for subj, points in cs408_advisor.KNOWLEDGE_MAP.items():
        with st.expander(f"📖 {subj}　（{len(points)} 个考点模块）"):
            cols = st.columns(2, gap="medium")
            for i, p in enumerate(points):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="zb-card" style="padding:11px 14px;margin-bottom:8px">'
                        f'<div class="zb-card-body" style="color:{PAL["text"]}">{p}</div></div>',
                        unsafe_allow_html=True,
                    )

# ============================================================
# Tab2: 经典例题
# ============================================================
with tab2:
    st.markdown("#### 经典例题")
    c1, c2 = st.columns([1.4, 3])
    with c1:
        subj_filter = st.selectbox("筛选科目", ["全部"] + cs408_advisor.SUBJECTS, key="ex_filter")

    pool = cs408_advisor.QUESTIONS
    if subj_filter != "全部":
        pool = [q for q in pool if q["subject"] == subj_filter]

    st.caption(f"共 **{len(pool)}** 道题")

    for i, q in enumerate(pool):
        with st.expander(f"[{q['subject']}·{q['topic']}] {q['question']}"):
            cc1, cc2 = st.columns(2, gap="medium")
            with cc1:
                st.markdown(
                    f'<div class="zb-card" style="border-left:3px solid #4E8A49">'
                    f'<div class="zb-card-title" style="color:#4E8A49">✅ 答案</div>'
                    f'<div class="zb-card-body" style="color:{PAL["text"]}">{q["answer"]}</div></div>',
                    unsafe_allow_html=True,
                )
            with cc2:
                st.markdown(
                    f'<div class="zb-card" style="border-left:3px solid {PAL["primary"]}">'
                    f'<div class="zb-card-title">💡 解析</div>'
                    f'<div class="zb-card-body" style="color:{PAL["text"]}">{q["analysis"]}</div></div>',
                    unsafe_allow_html=True,
                )

            already = wrongbook.exists(q["subject"], q["question"])
            if already:
                st.caption("✅ 已加入错题本")
            else:
                if st.button("➕ 加入错题本", key=f"add_{i}_{q['subject']}_{q['topic']}"):
                    wrongbook.add_wrong(
                        subject=q["subject"], question=q["question"], topic=q["topic"],
                        answer=q["answer"], analysis=q["analysis"], source="经典例题",
                    )
                    st.success("已加入错题本，去「📕 错题本」复习吧~")
                    st.rerun()

# ============================================================
# Tab3: AI讲题
# ============================================================
with tab3:
    st.markdown("#### 贴一道题，让 AI 老师讲明白")
    c1, c2 = st.columns([1.4, 3])
    with c1:
        subject = st.selectbox("科目", cs408_advisor.SUBJECTS, key="ai_subject")
    with c2:
        st.caption("支持拍照转文字后粘贴，或直接打字")

    q_text = st.text_area(
        "题目内容", height=150, label_visibility="collapsed",
        placeholder="例如：已知某分页系统，页面大小4KB，逻辑地址32位...",
        key="ai_qtext",
    )

    if st.button("开始讲解") and q_text.strip():
        if not config.is_configured():
            st.warning(config.config_hint())
        else:
            with st.spinner("AI老师在写板书..."):
                try:
                    result = cs408_advisor.explain_question(q_text, subject)
                    st.markdown(
                        f'<div class="zb-card" style="border-left:4px solid {PAL["primary"]}">'
                        f'<div class="zb-card-body" style="color:{PAL["text"]};white-space:pre-wrap">{result}</div></div>',
                        unsafe_allow_html=True,
                    )
                    st.session_state["_last_explain"] = {
                        "subject": subject, "question": q_text, "analysis": result,
                    }
                except Exception as e:
                    st.error(f"AI 讲解失败：{e}\n\n请检查网络或 API Key 是否有效。")

    last = st.session_state.get("_last_explain")
    if last:
        st.divider()
        st.caption("这道题做错了吗？可以存进错题本，之后反复看。")
        if st.button("➕ 把刚才这道题加入错题本", key="add_last"):
            wrongbook.add_wrong(
                subject=last["subject"], question=last["question"],
                analysis=last["analysis"], source="AI讲题",
            )
            st.success("已加入错题本。")
            st.session_state.pop("_last_explain", None)
            st.rerun()

    st.info("💡 近十年真题可以在王道论坛、考研帮找到 PDF，把题目文字粘进来就能讲。")

# ============================================================
# Tab4: 错题本
# ============================================================
with tab4:
    st.markdown("#### 📕 我的错题本")

    s = wrongbook.stats()
    if s["total"] == 0:
        theme.empty("错题本还是空的。去「📝 经典例题」或「🤖 AI讲题」把做错的题加进来吧～")
    else:
        theme.stat_row([
            (str(s["total"]), "错题总数"),
            (str(s["unmastered"]), "待攻克"),
            (str(s["mastered"]), "已掌握"),
            (f"{round(s['mastered'] / s['total'] * 100)}%", "掌握率"),
        ])
        theme.divider(14)

        # 各科分布（进度条风格）
        if s["by_subject"]:
            st.markdown("##### 各科目错题分布")
            for r in s["by_subject"]:
                done = r["done"] or 0
                ratio = done / r["total"] if r["total"] else 0
                st.markdown(
                    f'<div class="zb-card" style="padding:11px 16px;margin-bottom:8px">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:6px">'
                    f'<span style="font-weight:600;color:{PAL["text"]}">{r["subject"]}</span>'
                    f'<span style="font-size:0.82rem;color:{PAL["text_sub"]}">{done}/{r["total"]} 已掌握</span></div>'
                    f'<div style="height:7px;background:{PAL["surface_alt"]};border-radius:999px;overflow:hidden">'
                    f'<div style="width:{ratio * 100:.0f}%;height:100%;background:{PAL["primary_grad"]}"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        f1, f2 = st.columns([1, 1])
        with f1:
            subj_sel = st.selectbox("按科目筛选", ["全部"] + cs408_advisor.SUBJECTS, key="wb_filter")
        with f2:
            only_un = st.checkbox("只看未掌握", value=True, key="wb_only_un")

        items = wrongbook.list_wrong(subj_sel, only_un)
        if not items:
            st.success("这个筛选下没有错题啦，很棒！🎉")
        else:
            for it in items:
                flag = "✅" if it["mastered"] else "📌"
                head = it["question"][:40] + ("..." if len(it["question"]) > 40 else "")
                with st.expander(f"{flag} [{it['subject']}] {head}"):
                    st.markdown(f"**题目**：{it['question']}")
                    if it["my_answer"]:
                        st.markdown(f"**我的答案**：{it['my_answer']}")
                    if it["answer"]:
                        st.markdown(f"**正确答案**：{it['answer']}")
                    if it["analysis"]:
                        st.markdown(f"**解析**：{it['analysis']}")
                    st.caption(
                        f"来源：{it['source']} · 加入时间：{it['ts']}"
                        + (f" · 错因：{it['reason']}" if it["reason"] else "")
                    )

                    with st.form(f"note_form_{it['id']}"):
                        cc1, cc2 = st.columns([1, 2])
                        with cc1:
                            reason = st.selectbox(
                                "错因", ["未填写"] + wrongbook.ERROR_REASONS,
                                index=(wrongbook.ERROR_REASONS.index(it["reason"]) + 1)
                                if it["reason"] in wrongbook.ERROR_REASONS else 0,
                                key=f"reason_{it['id']}",
                            )
                        with cc2:
                            note = st.text_input("笔记 / 心得", value=it["note"] or "",
                                                 key=f"note_{it['id']}")
                        if st.form_submit_button("💾 保存"):
                            wrongbook.update_note(
                                it["id"], reason="" if reason == "未填写" else reason, note=note,
                            )
                            st.success("已保存。")
                            st.rerun()

                    b1, b2 = st.columns([1, 1])
                    with b1:
                        if it["mastered"]:
                            if st.button("↩️ 标记为未掌握", key=f"unmaster_{it['id']}"):
                                wrongbook.set_mastered(it["id"], False)
                                st.rerun()
                        else:
                            if st.button("🎉 我掌握了", key=f"master_{it['id']}"):
                                wrongbook.set_mastered(it["id"], True)
                                st.rerun()
                    with b2:
                        if st.button("🗑️ 删除", key=f"del_{it['id']}"):
                            wrongbook.delete_wrong(it["id"])
                            st.rerun()
