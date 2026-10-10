"""
② 心情周报可视化页
启动 streamlit run app.py 后，左侧导航会出现这个页面。
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from core import emotion_tracker

st.set_page_config(page_title="心情周报", page_icon="🐱")
st.title("🐱 猫猫的心情周报")
st.caption("知心猫猫帮你记下的情绪小曲线")

rows = emotion_tracker.fetch_recent(days=7)
if not rows:
    st.info("还没有对话记录，去主页面聊几句再来看看吧～")
    st.stop()

df = pd.DataFrame(rows)
df["ts"] = pd.to_datetime(df["ts"])
df["date"] = df["ts"].dt.date

emotion_cn = {
    "joy": "开心", "calm": "平静", "anxiety": "焦虑",
    "sadness": "难过", "anger": "愤怒", "confusion": "迷茫",
}
df["情绪"] = df["emotion"].map(emotion_cn).fillna(df["emotion"])

# 1. 情绪分布饼图
st.subheader("本周情绪分布")
fig1 = px.pie(df, names="情绪", hole=0.4)
st.plotly_chart(fig1, use_container_width=True)

# 2. 每日情绪折线
st.subheader("每日情绪趋势")
daily = df.groupby(["date", "emotion"]).size().reset_index(name="次数")
fig2 = px.line(daily, x="date", y="次数", color="emotion", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# 3. 最近对话回顾
st.subheader("最近说过的话")
st.dataframe(df[["ts", "情绪", "user_text"]].tail(10), use_container_width=True)
