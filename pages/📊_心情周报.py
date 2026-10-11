"""
② 心情周报可视化页（治愈暖色风）
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import emotion_tracker, theme

st.set_page_config(page_title="心情周报", page_icon="🐱", layout="centered")
theme.apply_warm()

PAL = theme.palette("warm")
EMO_CN = theme.EMOTION_CN
EMO_COLOR = theme.EMOTION_COLORS

# 情绪 → 心情分值（越高越正向），用于画趋势曲线
EMO_SCORE = {"joy": 5, "calm": 4, "confusion": 3, "anxiety": 2, "anger": 1.6, "sadness": 1}

theme.hero("🐱 猫猫的心情周报", "知心猫猫帮你记下的情绪小曲线")

# ===== 时间范围切换 =====
range_label = st.radio(
    "查看范围", ["最近 7 天", "最近 14 天", "最近 30 天"],
    horizontal=True, label_visibility="collapsed",
)
DAYS = {"最近 7 天": 7, "最近 14 天": 14, "最近 30 天": 30}[range_label]

rows = emotion_tracker.fetch_recent(days=DAYS)

if not rows:
    theme.empty("还没有对话记录，去主页面和猫猫聊几句，这里就会长出小曲线啦 🐾")
    st.stop()

df = pd.DataFrame(rows)
df["ts"] = pd.to_datetime(df["ts"])
df["date"] = df["ts"].dt.date
df["情绪"] = df["emotion"].map(EMO_CN).fillna(df["emotion"])

# ===== 顶部统计 =====
dominant = df["情绪"].value_counts()
dominant_name = dominant.index[0]
dominant_cnt = int(dominant.iloc[0])

# 需要关注：低落类情绪占比
_neg = df["emotion"].isin(["sadness", "anxiety", "anger"]).mean()
if _neg >= 0.5:
    mood_hint, hint_label = "偏低", "需要多陪陪"
elif _neg >= 0.25:
    mood_hint, hint_label = "一般", "还算平稳"
else:
    mood_hint, hint_label = "不错", "状态挺好"

theme.stat_row([
    (str(len(df)), f"{range_label}记录数"),
    (dominant_name, "出现最多的情绪"),
    (f"{dominant_cnt} 次", "最高频情绪次数"),
    (mood_hint, hint_label),
])

theme.divider(18)

# ===== 情绪分布 + 趋势 =====
col_left, col_right = st.columns([1, 1.35], gap="medium")

with col_left:
    st.markdown("#### 情绪分布")
    counts = df["情绪"].value_counts()
    order = [EMO_CN[k] for k in EMO_COLOR if EMO_CN[k] in counts.index]
    counts = counts.reindex(order).dropna()
    colors = [next((EMO_COLOR[k] for k, v in EMO_CN.items() if v == name), PAL["primary"])
              for name in counts.index]

    fig1 = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent", textfont=dict(size=12),
        hovertemplate="%{label}：%{value} 次（%{percent}）<extra></extra>",
    ))
    fig1.update_layout(
        showlegend=False, height=320,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=PAL["font"], color=PAL["text"]),
        annotations=[dict(text=f"共 {len(df)} 次", x=0.5, y=0.5,
                          font=dict(size=15, color=PAL["primary_dark"]), showarrow=False)],
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.markdown("#### 心情走势")
    daily = df.copy()
    daily["score"] = daily["emotion"].map(EMO_SCORE).fillna(3)
    by_day = daily.groupby("date", as_index=False)["score"].mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=by_day["date"], y=by_day["score"],
        mode="lines+markers",
        line=dict(color=PAL["primary"], width=3, shape="spline"),
        marker=dict(size=9, color=PAL["primary"],
                    line=dict(color="#FFFFFF", width=2)),
        fill="tozeroy", fillcolor="rgba(255,140,90,0.12)",
        hovertemplate="%{x}<br>心情分值 %{y:.1f}<extra></extra>",
    ))
    fig2.update_layout(
        height=320, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=PAL["font"], color=PAL["text"]),
        yaxis=dict(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5],
                   ticktext=["很难过", "焦虑", "迷茫", "还行", "开心"],
                   gridcolor=PAL["border"], zeroline=False),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ===== 最近对话回顾 =====
st.markdown(f"#### 最近说过的话（{range_label}）")
tail = df.sort_values("ts", ascending=False).head(10)

for _, r in tail.iterrows():
    emo = r["情绪"]
    color = next((EMO_COLOR[k] for k, v in EMO_CN.items() if v == emo), PAL["primary"])
    theme.card(
        title=f"{emo}　<span style='font-weight:400;font-size:0.82rem;color:{PAL['text_sub']}'>"
              f"{r['ts'].strftime('%m-%d %H:%M')}</span>",
        body=str(r["user_text"] or "（无内容）")[:80],
        tags=[(emo, "default")],
    )

st.caption("💡 情绪标签由猫猫在每轮对话中自动识别，仅供自我觉察参考，不构成医学评估。")
