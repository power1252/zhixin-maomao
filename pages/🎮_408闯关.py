"""
🎮 408 闯关小游戏 · 像素风（8-bit / NES 风格）

界面与角色设计参考 GitHub 开源项目：
  - NES.css (nostalgic-css) / 8bitcn-ui  → 8-bit 组件语言：0 圆角、硬阴影、像素字体
  - Pxlkit (joangeldelarosa)             → 像素图标包（gamification：星星/关卡）
  - pixelcat (toddsherman) / Pixie-Cat   → 像素猫吉祥物角色设计
缺失的位图素材（猫吉祥物、星星、四科图标）由 AI 以像素风生成，存于 assets/。

功能：关卡地图（逐关解锁/星级）· 选择题闯关（洗牌+即时反馈+错题入本）· 进度可视化
数据：data/cs408_quiz.json；进度落 SQLite（core/game_progress.py）
"""
import base64
import random
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from core import cs408_advisor, game_progress, theme, wrongbook

st.set_page_config(page_title="408闯关", page_icon="🎮", layout="wide")
theme.apply_pixel()

PAL = theme.palette("pixel")
SUBJECTS = cs408_advisor.SUBJECTS
ASSETS = Path(__file__).parent.parent / "assets"
CAT_IMG = ASSETS / "pixel_cat.png"
STAR_IMG = ASSETS / "pixel_star.png"
ICONS = {
    "数据结构": ASSETS / "pixel_subject_ds.png",
    "计算机组成原理": ASSETS / "pixel_subject_co.png",
    "操作系统": ASSETS / "pixel_subject_os.png",
    "数据库": ASSETS / "pixel_subject_db.png",
}


@lru_cache(maxsize=16)
def _uri(path: str) -> str:
    """把位图读成 data-URI，便于内联进 HTML 卡片（像素风整齐排布）。"""
    try:
        return "data:image/png;base64," + base64.b64encode(
            Path(path).read_bytes()).decode()
    except Exception:
        return ""


def _load_quiz():
    by_subject = {s: [] for s in SUBJECTS}
    for q in cs408_advisor.QUIZ:
        if q["subject"] in by_subject:
            by_subject[q["subject"]].append(q)
    return by_subject


def _prepare(subject: str) -> list[dict]:
    out = []
    for q in QUIZ[subject]:
        opts = [(o, False) for o in q["options"]]
        correct_text = q["options"][q["answer"]]
        random.shuffle(opts)
        out.append({
            "question": q["question"], "topic": q["topic"],
            "analysis": q["analysis"], "correct_text": correct_text, "opts": opts,
        })
    return out


def _stars(n: int) -> str:
    """像素风星级：满星用亮黄 ★，空星用暗色 ☆。"""
    return (f'<span style="color:{PAL["primary"]}">' + "★" * n + "</span>"
            f'<span style="color:{PAL["text_sub"]}">' + "☆" * (3 - n) + "</span>")


def _stars_plain(n: int) -> str:
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
        line=dict(color=PAL["primary"], width=2), fillcolor="rgba(255,205,117,0.25)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=wb_vals + [wb_vals[0]], theta=cats, fill="toself", name="错题掌握率",
        line=dict(color=PAL["ok"], width=2), fillcolor="rgba(56,183,100,0.22)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9),
                            gridcolor="#3b4261", color=PAL["text_sub"]),
            angularaxis=dict(tickfont=dict(size=11, color=PAL["text"]), gridcolor="#3b4261"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True, legend=dict(orientation="h", y=-0.08, font=dict(size=10)),
        margin=dict(l=40, r=40, t=20, b=40), height=360,
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=PAL["text"]),
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
                marker_color=PAL["primary"], marker_line_color=PAL["border"],
                marker_line_width=1.5)
    fig.add_bar(y=SUBJECTS, x=wb_vals, name="错题掌握率", orientation="h",
                marker_color=PAL["ok"], marker_line_color=PAL["border"],
                marker_line_width=1.5)
    fig.update_layout(
        barmode="group", height=320, margin=dict(l=40, r=20, t=10, b=10),
        legend=dict(orientation="h", y=-0.12, font=dict(size=10)),
        xaxis=dict(range=[0, 100], ticksuffix="%", gridcolor="#3b4261",
                   color=PAL["text_sub"]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", color=PAL["text"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PAL["text"]),
    )
    return fig


# ============================================================
# 顶部：像素吉祥物 + 标题（Title Screen）
# ============================================================
QUIZ = _load_quiz()
ov = game_progress.overall()

hc1, hc2 = st.columns([1, 4])
with hc1:
    if CAT_IMG.exists():
        st.image(str(CAT_IMG), width=120)
with hc2:
    st.markdown(
        f'<div class="zb-hero" style="margin-bottom:0">'
        f'<div class="zb-hero-title">🎮 408 闯关</div>'
        f'<div class="zb-hero-sub">像素风闯关 · 四科逐关解锁 · 答对得星 · 错题一键入本</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
theme.divider(16)

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
st.caption("第一关默认解锁，通关（≥1 星）后解锁下一关。每关 4 题，正确率越高星星越多（≥90%=3星 / ≥70%=2星 / ≥50%=1星）。")

if not st.session_state.get("game_active"):
    cols = st.columns(len(SUBJECTS))
    for i, subj in enumerate(SUBJECTS):
        unlocked = game_progress.is_unlocked(subj, SUBJECTS)
        best = game_progress.best_stars(subj)
        qcount = len(QUIZ[subj])
        icon_uri = _uri(str(ICONS.get(subj, "")))
        lock_badge = "" if unlocked else "🔒"
        with cols[i]:
            st.markdown(
                f'<div class="px-tile{" locked" if not unlocked else ""}">'
                f'<img src="{icon_uri}" style="width:76px;height:76px;image-rendering:pixelated;'
                f'filter:{"grayscale(0.7) brightness(0.7)" if not unlocked else "none"}"/>'
                f'<div style="font-family:{PAL["font"]};font-size:0.72rem;color:{PAL["text"]};'
                f'margin:10px 0 6px">{lock_badge} {subj}</div>'
                f'<div style="font-size:1.15rem;letter-spacing:2px">{_stars(best)}</div>'
                f'<div style="font-size:0.72rem;color:{PAL["text_sub"]};margin-top:6px">'
                f'{qcount} 题 · 最高 {best} 星</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            theme.divider(8)
            if unlocked:
                if st.button("▶ 开始挑战", key=f"start_{subj}", use_container_width=True):
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

    st.markdown(f"<div style='font-family:{PAL['font']};color:{PAL['text_sub']};font-size:0.72rem'>"
                f"LEVEL: {subj}</div>", unsafe_allow_html=True)

    if idx < total:
        q = qs[idx]
        st.progress(idx / total)
        st.markdown(
            f"<div style='font-family:{PAL['font']};font-size:0.72rem;color:{PAL['text']};margin:6px 0'>"
            f"第 {idx + 1} / {total} 题 · {q['topic']}　|　本轮正确 {st.session_state.game_correct}/{idx}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="zb-card" style="border-left:8px solid {PAL["primary_dark"]}">'
            f'<div class="zb-card-title">❓ {q["question"]}</div></div>',
            unsafe_allow_html=True,
        )

        selected = st.session_state.game_selected
        if selected is None:
            for oi, (text, _c) in enumerate(q["opts"]):
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
            for text, _c in q["opts"]:
                if text == q["correct_text"]:
                    bg, bd = "rgba(56,183,100,0.28)", PAL["ok"]
                elif text == selected and not ok:
                    bg, bd = "rgba(177,62,83,0.28)", PAL["bad"]
                else:
                    bg, bd = PAL["surface_alt"], PAL["border"]
                mark = " ✅" if text == q["correct_text"] else (" ❌" if text == selected and not ok else "")
                st.markdown(
                    f'<div class="px-opt" style="background:{bg};border-color:{bd}">{text}{mark}</div>',
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
                            st.session_state.game_added.add(idx)

            st.markdown(
                f'<div class="zb-card" style="border-left:8px solid {PAL["text_sub"]}">'
                f'<div class="zb-card-title" style="color:{PAL["text_sub"]}">💡 解析</div>'
                f'<div class="zb-card-body">{q["analysis"]}</div></div>',
                unsafe_allow_html=True,
            )

            label = "下一题 →" if idx + 1 < total else "🏆 查看成绩"
            if st.button(label, key="next_q", use_container_width=True):
                st.session_state.game_idx += 1
                st.session_state.game_selected = None
                st.rerun()
    else:
        correct = st.session_state.game_correct
        stars = game_progress.stars_for_accuracy(correct, total)
        if not st.session_state.game_recorded:
            game_progress.record_play(subj, total, correct, stars)
            st.session_state.game_recorded = True

        msg = ("PERFECT! 满分通关" if stars == 3 else
               "GREAT! 继续冲满分" if stars == 2 else
               "CLEAR! 再练更稳" if stars == 1 else
               "就差一点，再来一次")
        star_row = ""
        if STAR_IMG.exists():
            star_row = "".join(
                f'<img src="{_uri(str(STAR_IMG))}" style="width:44px;image-rendering:pixelated;'
                f'opacity:{"1" if k < stars else "0.28"}"/>' for k in range(3))
        st.markdown(
            f'<div class="zb-hero" style="text-align:center">'
            f'<div class="zb-hero-title">{subj} · 通关！</div>'
            f'<div style="margin:12px 0">{star_row or _stars(stars)}</div>'
            f'<div class="zb-hero-sub">正确 {correct}/{total}（{round(correct / total * 100)}%）· {msg}</div>'
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
st.caption("综合「闯关正确率」与「错题本掌握率」，一眼看到四科强弱。")

gp_stats = game_progress.subject_stats()
wb = wrongbook.stats()
wb_by_subject = wb["by_subject"]
wb_map = {r["subject"]: r for r in wb_by_subject}

combined = []
for s in SUBJECTS:
    g = gp_stats.get(s)
    qa = (g["correct"] / g["total"] * 100) if (g and g["total"]) else None
    w = wb_map.get(s)
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
    f'<div class="zb-card" style="display:flex;align-items:center;gap:16px">'
    f'<div style="font-family:{PAL["font"]};font-size:1.4rem;color:{PAL["primary"]};'
    f'text-shadow:2px 2px 0 {PAL["border"]}">{round(overall_mastery)}%</div>'
    f'<div style="flex:1">'
    f'<div style="font-size:0.8rem;color:{PAL["text_sub"]};margin-bottom:6px">综合掌握度（闯关 + 错题本）</div>'
    f'<div class="px-bar"><div style="width:{overall_mastery:.0f}%"></div></div>'
    f'</div></div>',
    unsafe_allow_html=True,
)

g1, g2 = st.columns([1, 1])
with g1:
    st.plotly_chart(_radar_fig(gp_stats, wb_by_subject), use_container_width=True)
with g2:
    st.plotly_chart(_bar_fig(gp_stats, wb_by_subject), use_container_width=True)

st.caption("📌 雷达图：外圈越大掌握越好；柱状图：两维度横向对比。错题掌握率来自「💻 408专业课」的错题本。")

if ov["total_q"] == 0 and wb["total"] == 0:
    theme.empty("还没有任何闯关或错题记录～ 先去上方关卡地图玩一关，或到「💻 408专业课」加几道错题吧！")

st.caption("🎨 界面/角色设计参考 GitHub：NES.css、8bitcn-ui、Pxlkit、pixelcat；猫吉祥物与图标为 AI 生成的像素风素材。")
