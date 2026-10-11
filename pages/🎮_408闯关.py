"""
🎮 408 闯关小游戏（现代 SaaS 冷色风）

功能：
  - 关卡地图：四科各一关，逐关解锁，通关得星（1~3 星）
  - 选择题闯关：每题四选一、洗牌选项、即时反馈，答错可一键加入错题本
  - 进度可视化：四科雷达图（闯关正确率 vs 错题掌握率）+ 各科进度条 + 综合掌握度
数据：data/cs408_quiz.json；进度落 SQLite（core/game_progress.py）
"""
import random

import plotly.graph_objects as go
import streamlit as st

from core import cs408_advisor, game_progress, theme, wrongbook

st.set_page_config(page_title="408闯关", page_icon="🎮", layout="wide")
theme.apply_cool()

PAL = theme.palette("cool")
SUBJECTS = cs408_advisor.SUBJECTS


def _load_quiz():
    """按科目聚合题库。"""
    by_subject = {s: [] for s in SUBJECTS}
    for q in cs408_advisor.QUIZ:
        if q["subject"] in by_subject:
            by_subject[q["subject"]].append(q)
    return by_subject


def _prepare(subject: str) -> list[dict]:
    """抽取该科目题目，洗牌选项，标注正确项文本。"""
    out = []
    for q in QUIZ[subject]:
        opts = [(o, False) for o in q["options"]]
        correct_text = q["options"][q["answer"]]
        # 打散顺序，并记录每个选项是否正确
        random.shuffle(opts)
        out.append({
            "question": q["question"],
            "topic": q["topic"],
            "analysis": q["analysis"],
            "correct_text": correct_text,
            "opts": opts,
        })
    return out


def _stars(n: int) -> str:
    return "★" * n + "☆" * (3 - n)


def _radar_fig(gp_stats: dict, wb_by_subject: list[dict]) -> go.Figure:
    wb_map = {r["subject"]: r for r in wb_by_subject}
    quiz_vals, wb_vals = [], []
    for s in SUBJECTS:
        g = gp_stats.get(s)
        qa = (g["correct"] / g["total"] * 100) if (g and g["total"]) else 0.0
        w = wb_map.get(s)
        wm = (w["done"] / w["total"] * 100) if (w and w["total"]) else 0.0
        quiz_vals.append(round(qa, 1))
        wb_vals.append(round(wm, 1))

    cats = SUBJECTS + [SUBJECTS[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=quiz_vals + [quiz_vals[0]], theta=cats, fill="toself", name="闯关正确率",
        line_color="#2C5282", fillcolor="rgba(44,82,130,0.22)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=wb_vals + [wb_vals[0]], theta=cats, fill="toself", name="错题掌握率",
        line_color="#4E8A49", fillcolor="rgba(78,138,73,0.18)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10),
                            gridcolor=PAL["border"]),
            angularaxis=dict(tickfont=dict(size=12, color=PAL["text"])),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True, legend=dict(orientation="h", y=-0.08, font=dict(size=11)),
        margin=dict(l=40, r=40, t=20, b=40), height=360,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _bar_fig(gp_stats: dict, wb_by_subject: list[dict]) -> go.Figure:
    wb_map = {r["subject"]: r for r in wb_by_subject}
    quiz_vals, wb_vals = [], []
    for s in SUBJECTS:
        g = gp_stats.get(s)
        qa = (g["correct"] / g["total"] * 100) if (g and g["total"]) else 0.0
        w = wb_map.get(s)
        wm = (w["done"] / w["total"] * 100) if (w and w["total"]) else 0.0
        quiz_vals.append(round(qa, 1))
        wb_vals.append(round(wm, 1))

    fig = go.Figure()
    fig.add_bar(y=SUBJECTS, x=quiz_vals, name="闯关正确率", orientation="h",
                marker_color="#2C5282")
    fig.add_bar(y=SUBJECTS, x=wb_vals, name="错题掌握率", orientation="h",
                marker_color="#4E8A49")
    fig.update_layout(
        barmode="group", height=300, margin=dict(l=40, r=20, t=10, b=10),
        legend=dict(orientation="h", y=-0.12, font=dict(size=11)),
        xaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=PAL["border"]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PAL["text"]),
    )
    return fig


# ============================================================
# 顶部 Hero + 统计
# ============================================================
theme.hero("🎮 408 闯关小游戏", "四科逐关解锁 · 选择题闯关得星 · 通关错题一键入本")

QUIZ = _load_quiz()
ov = game_progress.overall()

theme.stat_row([
    (f"{ov['total_stars']} / {len(SUBJECTS) * game_progress.STARS_PER_LEVEL}", "⭐ 累计星星"),
    (f"{ov['subjects_played']} / {len(SUBJECTS)}", "🏁 已通关科目"),
    (f"{round(ov['correct_q'] / ov['total_q'] * 100) if ov['total_q'] else 0}%", "🎯 累计正确率"),
    (str(ov["total_q"]), "📝 累计答题"),
])
theme.divider(14)

# ============================================================
# 关卡地图
# ============================================================
st.markdown("#### 🗺️ 关卡地图")
st.caption("第一关默认解锁，通关（≥1 星）后解锁下一关。每关 4 题，正确率越高星星越多。")

if st.session_state.get("game_active"):
    # —— 游戏中：渲染答题界面，跳过关卡地图 ——
    pass
else:
    cols = st.columns(len(SUBJECTS))
    for i, subj in enumerate(SUBJECTS):
        unlocked = game_progress.is_unlocked(subj, SUBJECTS)
        best = game_progress.best_stars(subj)
        qcount = len(QUIZ[subj])
        with cols[i]:
            lock = "" if unlocked else " 🔒"
            st.markdown(
                f'<div class="zb-card" style="text-align:center;padding:18px 12px">'
                f'<div style="font-size:1.05rem;font-weight:700;color:{PAL["text"]}">{subj}{lock}</div>'
                f'<div style="margin:8px 0;font-size:1.4rem;color:#F5A623">{_stars(best)}</div>'
                f'<div style="font-size:0.8rem;color:{PAL["text_sub"]}">{qcount} 题 · 最高 {best} 星</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if unlocked:
                if st.button(f"▶ 开始挑战", key=f"start_{subj}", use_container_width=True):
                    st.session_state.game_active = True
                    st.session_state.game_subject = subj
                    st.session_state.game_questions = _prepare(subj)
                    st.session_state.game_idx = 0
                    st.session_state.game_correct = 0
                    st.session_state.game_selected = None
                    st.session_state.game_recorded = False
                    st.session_state.game_added = set()
                    st.session_state.game_results = []
                    st.rerun()
            else:
                st.caption("🔒 先通关上一关")

# ============================================================
# 答题界面
# ============================================================
if st.session_state.get("game_active"):
    subj = st.session_state.game_subject
    qs = st.session_state.game_questions
    idx = st.session_state.game_idx
    total = len(qs)

    if st.button("⏏️ 退出本关", key="quit_game"):
        for k in ("game_active", "game_subject", "game_questions", "game_idx",
                  "game_correct", "game_selected", "game_recorded", "game_added",
                  "game_results"):
            st.session_state.pop(k, None)
        st.rerun()

    if idx < total:
        q = qs[idx]
        st.progress((idx) / total)
        st.markdown(f"**第 {idx + 1} / {total} 题 · {q['topic']}**　"
                    f"本轮正确：{st.session_state.game_correct}/{idx}")

        with st.container():
            st.markdown(
                f'<div class="zb-card" style="border-left:4px solid {PAL["primary"]}">'
                f'<div class="zb-card-title">❓ {q["question"]}</div></div>',
                unsafe_allow_html=True,
            )

            selected = st.session_state.game_selected
            if selected is None:
                for oi, (text, _is_corr) in enumerate(q["opts"]):
                    if st.button(text, key=f"opt_{idx}_{oi}", use_container_width=True):
                        st.session_state.game_selected = text
                        if text == q["correct_text"]:
                            st.session_state.game_correct += 1
                        st.session_state.game_results.append({
                            "question": q["question"], "selected": text,
                            "correct": q["correct_text"], "ok": text == q["correct_text"],
                        })
                        st.rerun()
            else:
                ok = selected == q["correct_text"]
                for text, _ in q["opts"]:
                    if text == q["correct_text"]:
                        style = "background:#E3F2E1;border:1px solid #4E8A49;color:#2f5d2c"
                    elif text == selected and not ok:
                        style = "background:#FDE8E8;border:1px solid #D96C6C;color:#9b3b3b"
                    else:
                        style = "background:#F2F5FA;border:1px solid #E2E8F0;color:#64748B"
                    st.markdown(
                        f'<div style="padding:9px 14px;margin-bottom:8px;border-radius:8px;{style}">'
                        f'{text}{" ✅" if text == q["correct_text"] else (" ❌" if text == selected and not ok else "")}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                if ok:
                    st.success("✅ 回答正确！")
                else:
                    st.error(f"❌ 答错了，正确答案是：**{q['correct_text']}**")
                    if idx not in st.session_state.game_added:
                        if st.button("➕ 加入错题本", key=f"add_{idx}"):
                            if not wrongbook.exists(subj, q["question"]):
                                wrongbook.add_wrong(
                                    subject=subj, question=q["question"],
                                    answer=q["correct_text"], analysis=q["analysis"],
                                    topic=q["topic"], source="闯关小游戏",
                                )
                                st.session_state.game_added.add(idx)
                                st.success("已加入错题本，去「💻 408专业课 → 📕 错题本」复习吧~")
                                st.rerun()
                            else:
                                st.caption("这道题已在错题本里啦。")
                                st.session_state.game_added.add(idx)

                st.markdown(
                    f'<div class="zb-card" style="border-left:3px solid {PAL["text_sub"]}">'
                    f'<div class="zb-card-title" style="color:{PAL["text_sub"]}">💡 解析</div>'
                    f'<div class="zb-card-body">{q["analysis"]}</div></div>',
                    unsafe_allow_html=True,
                )

                if idx + 1 < total:
                    if st.button("下一题 →", key="next_q", use_container_width=True):
                        st.session_state.game_idx += 1
                        st.session_state.game_selected = None
                        st.rerun()
                else:
                    if st.button("🏆 查看成绩", key="finish_q", use_container_width=True):
                        st.session_state.game_idx += 1
                        st.session_state.game_selected = None
                        st.rerun()
    else:
        # —— 通关结算 ——
        correct = st.session_state.game_correct
        stars = game_progress.stars_for_accuracy(correct, total)
        if not st.session_state.game_recorded:
            game_progress.record_play(subj, total, correct, stars)
            st.session_state.game_recorded = True

        msg = ("太强了！满分通关 🎉" if stars == 3 else
               "稳！继续冲满分 💪" if stars == 2 else
               "过关啦，再练练更稳 🐱" if stars == 1 else
               "差一点，再来一次就过 🔥")
        st.markdown(
            f'<div class="zb-hero" style="text-align:center">'
            f'<div class="zb-hero-title">{subj} 通关！</div>'
            f'<div style="font-size:2.2rem;color:#FFD66B;margin:8px 0">{_stars(stars)}</div>'
            f'<div class="zb-hero-sub">正确 {correct}/{total}（{round(correct/total*100)}%）· {msg}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 再玩一次", key="replay", use_container_width=True):
                st.session_state.game_questions = _prepare(subj)
                st.session_state.game_idx = 0
                st.session_state.game_correct = 0
                st.session_state.game_selected = None
                st.session_state.game_recorded = False
                st.session_state.game_added = set()
                st.session_state.game_results = []
                st.rerun()
        with c2:
            if st.button("🗺️ 返回关卡地图", key="back_map", use_container_width=True):
                for k in ("game_active", "game_subject", "game_questions", "game_idx",
                          "game_correct", "game_selected", "game_recorded", "game_added",
                          "game_results"):
                    st.session_state.pop(k, None)
                st.rerun()

theme.divider(22)

# ============================================================
# 408 学习进度可视化
# ============================================================
st.markdown("#### 📊 408 学习进度可视化")
st.caption("综合「闯关正确率」与「错题本掌握率」，帮你一眼看到四科强弱。")

gp_stats = game_progress.subject_stats()
wb = wrongbook.stats()
wb_by_subject = wb["by_subject"]

# 综合掌握度（仅在至少一方有数据时计算）
combined = []
for s in SUBJECTS:
    g = gp_stats.get(s)
    qa = (g["correct"] / g["total"] * 100) if (g and g["total"]) else None
    w = {r["subject"]: r for r in wb_by_subject}.get(s)
    wm = (w["done"] / w["total"] * 100) if (w and w["total"]) else None
    if qa is not None and wm is not None:
        combined.append(0.6 * qa + 0.4 * wm)
    elif qa is not None:
        combined.append(qa)
    elif wm is not None:
        combined.append(wm)
    else:
        combined.append(0.0)
overall_mastery = sum(combined) / len(combined)

st.markdown(
    f'<div class="zb-card" style="display:flex;align-items:center;gap:14px;margin-bottom:14px">'
    f'<div style="font-size:1.6rem;font-weight:700;color:{PAL["primary"]}">'
    f'{round(overall_mastery)}%</div>'
    f'<div style="flex:1">'
    f'<div style="font-size:0.85rem;color:{PAL["text_sub"]};margin-bottom:5px">综合掌握度（闯关+错题本）</div>'
    f'<div style="height:9px;background:{PAL["surface_alt"]};border-radius:999px;overflow:hidden">'
    f'<div style="width:{overall_mastery:.0f}%;height:100%;background:{PAL["primary_grad"]}"></div>'
    f'</div></div></div>',
    unsafe_allow_html=True,
)

g1, g2 = st.columns([1, 1])
with g1:
    st.plotly_chart(_radar_fig(gp_stats, wb_by_subject), use_container_width=True)
with g2:
    st.plotly_chart(_bar_fig(gp_stats, wb_by_subject), use_container_width=True)

st.caption("📌 雷达图：外圈越大表示该科掌握越好；柱状图：横向对比两维度。错题掌握率来自「💻 408专业课」里的错题本。")

if ov["total_q"] == 0 and wb["total"] == 0:
    theme.empty("还没有任何闯关或错题记录～ 先去上方关卡地图玩一关，或到「💻 408专业课」加几道错题吧！")
