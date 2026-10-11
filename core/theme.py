"""
统一 UI 设计系统。

两套主题（遵循 PROJECT.md 双主题规范）：
  - WARM  治愈暖色：聊天主页、心情周报
  - COOL  现代 SaaS 冷色：考研咨询、408 专业课

用法：
    from core import theme
    theme.apply_warm()          # 或 theme.apply_cool()
    theme.hero("🐱 知心猫猫", "副标题")
    theme.card_open(); ...; theme.card_close()

设计令牌集中在 _WARM / _COOL 两个字典里，改配色只动这里。
"""
import streamlit as st

# ============================================================
# 设计令牌
# ============================================================

_WARM = {
    "name": "warm",
    # 背景
    "bg": "linear-gradient(160deg, #FFFBF7 0%, #FFF3E9 55%, #FFEADB 100%)",
    "surface": "#FFFFFF",
    "surface_alt": "#FFF7F1",
    "sidebar": "#FFF4EA",
    # 主色
    "primary": "#FF8C5A",
    "primary_dark": "#E07B4F",
    "primary_soft": "#FFE3D3",
    "primary_grad": "linear-gradient(135deg, #FFB18A 0%, #FF8C5A 100%)",
    # 文本
    "text": "#3D2C29",
    "text_sub": "#8A7268",
    # 描边 / 阴影
    "border": "#F5E3D8",
    "shadow": "0 2px 10px rgba(224, 123, 79, 0.08)",
    "shadow_hover": "0 6px 20px rgba(224, 123, 79, 0.16)",
    "radius": "18px",
    "radius_sm": "12px",
    "font": '"PingFang SC", "Microsoft YaHei", -apple-system, sans-serif',
}

_COOL = {
    "name": "cool",
    "bg": "#F7F9FC",
    "surface": "#FFFFFF",
    "surface_alt": "#F2F5FA",
    "sidebar": "#FFFFFF",
    "primary": "#2C5282",
    "primary_dark": "#1E3A5F",
    "primary_soft": "#E8EFF8",
    "primary_grad": "linear-gradient(135deg, #3A6EA5 0%, #2C5282 100%)",
    "text": "#1A2B42",
    "text_sub": "#64748B",
    "border": "#E2E8F0",
    "shadow": "0 1px 3px rgba(16, 30, 54, 0.06), 0 1px 2px rgba(16, 30, 54, 0.04)",
    "shadow_hover": "0 6px 20px rgba(16, 30, 54, 0.10)",
    "radius": "12px",
    "radius_sm": "8px",
    "font": '"PingFang SC", "Microsoft YaHei", -apple-system, sans-serif',
}

# 像素风（8-bit / NES 风格，参考 NES.css、8bitcn/ui 的设计语言：
# 0 圆角、硬阴影、有限调色板、Press Start 2P 像素字体）
_PIXEL = {
    "name": "pixel",
    # 背景：深蓝底 + 网格
    "bg": "#1a1c2c",
    "surface": "#29366f",
    "surface_alt": "#1f2547",
    "sidebar": "#14172b",
    # 主色：橙(按钮) + 黄(高亮/数字)
    "primary": "#ffcd75",
    "primary_dark": "#ef7d57",
    "primary_soft": "#333c57",
    "primary_grad": "#ef7d57",
    # 文本
    "text": "#f4f4f4",
    "text_sub": "#94b0c2",
    # 描边（近黑）/ 硬阴影
    "border": "#0d0e1a",
    "shadow": "4px 4px 0 #0d0e1a",
    "shadow_hover": "6px 6px 0 #0d0e1a",
    "radius": "0px",
    "radius_sm": "0px",
    "font": '"Press Start 2P", "ZCOOL KuaiLe", "PingFang SC", "Microsoft YaHei", monospace',
    # 像素风专用色
    "panel": "#29366f",
    "panel_alt": "#333c57",
    "ok": "#38b764",
    "bad": "#b13e53",
    "warn": "#ffcd75",
}

# 情绪 → 配色（和谐化的分类色板，两套主题共用）
EMOTION_COLORS = {
    "joy": "#F5A623",
    "calm": "#7FB77E",
    "anxiety": "#E8985E",
    "sadness": "#7B9FD1",
    "anger": "#D96C6C",
    "confusion": "#A88FC7",
}

EMOTION_CN = {
    "joy": "开心", "calm": "平静", "anxiety": "焦虑",
    "sadness": "难过", "anger": "愤怒", "confusion": "迷茫",
}


# ============================================================
# 样式注入
# ============================================================

def _css(t: dict) -> str:
    """根据设计令牌生成全局 CSS。"""
    is_cool = t["name"] == "cool"
    return f"""
<style>
    /* ---------- 全局 ---------- */
    .stApp {{
        background: {t["bg"]};
        font-family: {t["font"]};
    }}
    .block-container {{
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1080px;
    }}
    h1, h2, h3, h4 {{
        font-family: {t["font"]};
        color: {t["primary"] if is_cool else t["primary_dark"]};
        letter-spacing: -0.01em;
    }}
    h1 {{ font-weight: 700; }}
    h2 {{ font-weight: 650; font-size: 1.35rem; }}
    h3 {{ font-weight: 600; font-size: 1.1rem; }}
    p, li, span, div {{ color: {t["text"]}; }}

    /* ---------- 侧边栏 ---------- */
    section[data-testid="stSidebar"] {{
        background: {t["sidebar"]};
        border-right: 1px solid {t["border"]};
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.5rem;
    }}

    /* ---------- 按钮 ---------- */
    .stButton > button, .stFormSubmitButton > button {{
        background: {t["primary_grad"]};
        color: #FFFFFF;
        border: none;
        border-radius: {t["radius_sm"]};
        padding: 0.5rem 1.1rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: {t["shadow"]};
        transition: all 0.18s ease;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        box-shadow: {t["shadow_hover"]};
        transform: translateY(-1px);
        color: #FFFFFF;
    }}
    .stButton > button:active {{ transform: translateY(0); }}
    /* 次要按钮（kind=secondary 通过 key 前缀降级处理见下） */
    .stDownloadButton > button {{
        background: {t["surface"]};
        color: {t["primary"]};
        border: 1px solid {t["border"]};
        border-radius: {t["radius_sm"]};
        font-weight: 600;
    }}

    /* ---------- 输入控件 ---------- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input {{
        border-radius: {t["radius_sm"]} !important;
        border-color: {t["border"]} !important;
        background: {t["surface"]} !important;
        color: {t["text"]} !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {t["primary"]} !important;
        box-shadow: 0 0 0 3px {t["primary_soft"]} !important;
    }}
    .stChatInputContainer {{
        border-radius: {t["radius"]} !important;
        border: 1px solid {t["border"]} !important;
        box-shadow: {t["shadow"]};
    }}

    /* ---------- 聊天消息 ---------- */
    .stChatMessage {{
        border-radius: {t["radius"]} !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
        background: {t["surface"]} !important;
        box-shadow: {t["shadow"]};
        border: 1px solid {t["border"]};
    }}

    /* ---------- 卡片元素 ---------- */
    .stExpander {{
        border: 1px solid {t["border"]} !important;
        border-radius: {t["radius_sm"]} !important;
        background: {t["surface"]} !important;
        box-shadow: {t["shadow"]};
        overflow: hidden;
    }}
    .stExpander summary {{
        font-weight: 600;
        color: {t["text"]};
    }}
    {"" if is_cool else f'''
    /* 暖色主题：expander 左侧暖色描边 */
    .stExpander {{ border-left: 4px solid {t["primary_soft"]} !important; }}
    '''}

    /* ---------- metric 指标卡 ---------- */
    div[data-testid="stMetric"] {{
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: {t["radius_sm"]};
        padding: 14px 18px;
        box-shadow: {t["shadow"]};
    }}
    div[data-testid="stMetricValue"] {{
        color: {t["primary"]};
        font-weight: 700;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {t["text_sub"]};
        font-size: 0.82rem;
    }}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 1px solid {t["border"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: {t["radius_sm"]} {t["radius_sm"]} 0 0;
        padding: 8px 16px;
        font-weight: 600;
        color: {t["text_sub"]};
        background: transparent;
    }}
    .stTabs [aria-selected="true"] {{
        color: {t["primary"]} !important;
        background: {t["primary_soft"]};
    }}

    /* ---------- 表格 ---------- */
    .stDataFrame, div[data-testid="stDataFrame"] {{
        border-radius: {t["radius_sm"]};
        overflow: hidden;
        border: 1px solid {t["border"]};
    }}

    /* ---------- 提示条 ---------- */
    div[data-testid="stAlert"] {{
        border-radius: {t["radius_sm"]};
        border: none;
        box-shadow: {t["shadow"]};
    }}
    hr {{ border-color: {t["border"]}; }}

    /* ---------- 自定义组件 ---------- */
    .zb-hero {{
        background: {t["primary_grad"]};
        border-radius: {t["radius"]};
        padding: 26px 30px;
        margin-bottom: 22px;
        box-shadow: {t["shadow_hover"]};
    }}
    .zb-hero-title {{
        color: #FFFFFF !important;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .zb-hero-sub {{
        color: rgba(255,255,255,0.92) !important;
        font-size: 0.93rem;
        margin: 6px 0 0 0;
    }}
    .zb-card {{
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: {t["radius_sm"]};
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: {t["shadow"]};
        transition: all 0.18s ease;
    }}
    .zb-card:hover {{
        box-shadow: {t["shadow_hover"]};
        transform: translateY(-2px);
        border-color: {t["primary_soft"]};
    }}
    .zb-card-title {{
        font-weight: 700;
        font-size: 1.02rem;
        color: {t["primary"]};
        margin-bottom: 4px;
    }}
    .zb-card-body {{
        font-size: 0.88rem;
        color: {t["text_sub"]};
        line-height: 1.6;
    }}
    .zb-tag {{
        display: inline-block;
        padding: 2px 9px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 600;
        background: {t["primary_soft"]};
        color: {t["primary"]};
        margin-right: 6px;
        margin-top: 2px;
    }}
    .zb-tag-warn {{ background: #FDEBD0; color: #B9770E; }}
    .zb-tag-ok {{ background: #E3F2E1; color: #4E8A49; }}
    .zb-tag-gray {{ background: {t["surface_alt"]}; color: {t["text_sub"]}; }}

    .zb-stat {{
        text-align: center;
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: {t["radius_sm"]};
        padding: 14px 8px;
        box-shadow: {t["shadow"]};
    }}
    .zb-stat-num {{
        font-size: 1.7rem;
        font-weight: 700;
        color: {t["primary"]};
        line-height: 1.1;
    }}
    .zb-stat-label {{
        font-size: 0.78rem;
        color: {t["text_sub"]};
        margin-top: 4px;
    }}

    .zb-empty {{
        text-align: center;
        padding: 40px 20px;
        color: {t["text_sub"]};
        background: {t["surface_alt"]};
        border: 1px dashed {t["border"]};
        border-radius: {t["radius"]};
        font-size: 0.92rem;
    }}

    /* ---------- 移动端适配 ---------- */
    @media (max-width: 768px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .zb-hero {{ padding: 18px 20px; }}
        .zb-hero-title {{ font-size: 1.35rem; }}
        .zb-hero-sub {{ font-size: 0.85rem; }}
        h1 {{ font-size: 1.5rem !important; }}
    }}
</style>
"""


def apply_warm():
    """注入治愈暖色主题（聊天页 / 心情周报）。"""
    st.markdown(_css(_WARM), unsafe_allow_html=True)


def apply_cool():
    """注入现代 SaaS 冷色主题（考研 / 408）。"""
    st.markdown(_css(_COOL), unsafe_allow_html=True)


def _pixel_css(t: dict) -> str:
    """像素风（8-bit / NES 风格）CSS。

    设计语言参考 GitHub 开源项目 NES.css / 8bitcn-ui：
    0 圆角、硬阴影(offset shadow)、有限复古调色板、Press Start 2P 像素字体、
    image-rendering:pixelated 保证位图素材锐利。
    """
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=ZCOOL+KuaiLe&display=swap');

    .stApp {{
        background-color: {t["bg"]};
        background-image:
            linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 16px 16px;
        font-family: "ZCOOL KuaiLe", "PingFang SC", "Microsoft YaHei", sans-serif;
        color: {t["text"]};
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1080px; }}

    h1, h2, h3, h4 {{
        font-family: {t["font"]};
        color: {t["primary"]};
        letter-spacing: 0;
        text-shadow: 2px 2px 0 {t["border"]};
    }}
    h1 {{ font-weight: 400; }}
    h2 {{ font-size: 1.05rem; }}
    h3 {{ font-size: 0.92rem; }}
    p, li, span, div {{ color: {t["text"]}; }}

    img {{ image-rendering: pixelated; }}

    section[data-testid="stSidebar"] {{
        background: {t["sidebar"]};
        border-right: 4px solid {t["border"]};
    }}

    /* 像素方按钮 + 硬阴影 + 按下位移 */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
        background: {t["primary_dark"]};
        color: #ffffff;
        border: 3px solid {t["border"]};
        border-radius: 0;
        padding: 0.55rem 1rem;
        font-family: {t["font"]};
        font-weight: 400;
        font-size: 0.78rem;
        box-shadow: {t["shadow"]};
        transition: none;
    }}
    .stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p {{
        font-family: {t["font"]};
        color: #ffffff;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
        background: {t["primary"]};
        color: {t["border"]};
        box-shadow: {t["shadow_hover"]};
        transform: translate(-2px,-2px);
    }}
    .stButton > button:hover p {{ color: {t["border"]}; }}
    .stButton > button:active {{ transform: translate(2px,2px); box-shadow: 0 0 0 {t["border"]}; }}

    /* 输入控件 */
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div {{
        border-radius: 0 !important;
        border: 3px solid {t["border"]} !important;
        background: {t["surface"]} !important;
        color: {t["text"]} !important;
        font-family: {t["font"]};
        box-shadow: {t["shadow"]};
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{ border-color: {t["primary"]} !important; }}

    /* 展开器 */
    .stExpander {{
        border: 3px solid {t["border"]} !important;
        border-radius: 0 !important;
        background: {t["surface"]} !important;
        box-shadow: {t["shadow"]};
        overflow: hidden;
    }}
    .stExpander summary {{ font-family: {t["font"]}; color: {t["text"]}; }}

    /* metric */
    div[data-testid="stMetric"] {{
        background: {t["surface"]};
        border: 3px solid {t["border"]};
        border-radius: 0;
        box-shadow: {t["shadow"]};
        padding: 14px 16px;
    }}
    div[data-testid="stMetricValue"] {{ color: {t["primary"]}; font-family: {t["font"]}; }}
    div[data-testid="stMetricLabel"] {{ color: {t["text_sub"]}; }}

    /* tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 3px solid {t["border"]}; }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 0; padding: 8px 14px;
        font-family: {t["font"]}; font-size: 0.76rem;
        color: {t["text_sub"]}; background: {t["panel_alt"]};
        border: 3px solid {t["border"]}; border-bottom: none;
    }}
    .stTabs [aria-selected="true"] {{ color: {t["border"]} !important; background: {t["primary"]}; }}

    /* 进度条 */
    .stProgress > div > div > div {{ background: {t["panel_alt"]}; border-radius: 0; border: 2px solid {t["border"]}; }}
    .stProgress > div > div > div > div {{ background: {t["primary"]}; border-radius: 0; }}

    /* 提示条 */
    div[data-testid="stAlert"] {{ border-radius: 0; border: 3px solid {t["border"]}; box-shadow: {t["shadow"]}; }}
    hr {{ border-color: {t["border"]}; }}

    /* ---------- 自定义组件（像素版） ---------- */
    .zb-hero {{
        background: {t["panel"]};
        border: 4px solid {t["border"]};
        border-radius: 0;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: {t["shadow_hover"]};
    }}
    .zb-hero-title {{
        color: {t["primary"]} !important;
        font-family: {t["font"]};
        font-size: 1.45rem;
        font-weight: 400;
        margin: 0;
        text-shadow: 3px 3px 0 {t["border"]};
        line-height: 1.5;
    }}
    .zb-hero-sub {{ color: {t["text"]} !important; font-size: 0.9rem; margin: 12px 0 0 0; }}
    .zb-card {{
        background: {t["surface"]};
        border: 3px solid {t["border"]};
        border-radius: 0;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: {t["shadow"]};
        transition: none;
    }}
    .zb-card:hover {{ box-shadow: {t["shadow_hover"]}; transform: translate(-2px,-2px); }}
    .zb-card-title {{
        font-family: {t["font"]};
        font-weight: 400;
        font-size: 0.82rem;
        color: {t["primary"]};
        margin-bottom: 6px;
        line-height: 1.7;
    }}
    .zb-card-body {{ font-size: 0.88rem; color: {t["text"]}; line-height: 1.7; }}
    .zb-tag {{
        display: inline-block; padding: 3px 9px; border-radius: 0;
        font-size: 0.72rem; font-weight: 400;
        background: {t["primary"]}; color: {t["border"]};
        border: 2px solid {t["border"]}; margin-right: 6px; margin-top: 2px;
    }}
    .zb-tag-warn {{ background: {t["warn"]}; color: {t["border"]}; }}
    .zb-tag-ok {{ background: {t["ok"]}; color: #ffffff; }}
    .zb-tag-gray {{ background: {t["panel_alt"]}; color: {t["text_sub"]}; }}

    .zb-stat {{
        text-align: center; background: {t["panel"]};
        border: 3px solid {t["border"]}; border-radius: 0;
        padding: 14px 8px; box-shadow: {t["shadow"]};
    }}
    .zb-stat-num {{
        font-family: {t["font"]}; font-size: 1.25rem;
        color: {t["primary"]}; line-height: 1.4;
        text-shadow: 2px 2px 0 {t["border"]};
    }}
    .zb-stat-label {{ font-size: 0.78rem; color: {t["text_sub"]}; margin-top: 6px; }}

    .zb-empty {{
        text-align: center; padding: 38px 20px; color: {t["text_sub"]};
        background: {t["surface_alt"]}; border: 3px dashed {t["text_sub"]};
        border-radius: 0; font-size: 0.9rem;
    }}

    /* 像素关卡卡（页面内联使用） */
    .px-tile {{
        background: {t["panel"]}; border: 3px solid {t["border"]};
        box-shadow: {t["shadow"]}; padding: 14px 10px; text-align: center; height: 100%;
    }}
    .px-tile.locked {{ background: {t["surface_alt"]}; }}
    .px-opt {{
        border: 3px solid {t["border"]}; border-radius: 0;
        padding: 11px 14px; margin-bottom: 9px; font-size: 0.9rem;
        box-shadow: 3px 3px 0 {t["border"]};
    }}
    .px-bar {{
        height: 16px; background: {t["panel_alt"]};
        border: 3px solid {t["border"]}; overflow: hidden;
    }}
    .px-bar > div {{ height: 100%; background: {t["primary"]}; }}

    @media (max-width: 768px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .zb-hero {{ padding: 16px 18px; }}
        .zb-hero-title {{ font-size: 1rem; }}
    }}
</style>
"""


def apply_pixel():
    """注入像素风（8-bit）主题——用于 408 闯关小游戏。"""
    st.markdown(_pixel_css(_PIXEL), unsafe_allow_html=True)


def palette(name: str = "warm") -> dict:
    """取出主题令牌，供 Plotly 等外部渲染使用。"""
    if name == "warm":
        return _WARM
    if name == "pixel":
        return _PIXEL
    return _COOL


# ============================================================
# 可复用组件
# ============================================================

def hero(title: str, subtitle: str = ""):
    """页面顶部渐变大标题条。"""
    sub = f'<p class="zb-hero-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="zb-hero"><p class="zb-hero-title">{title}</p>{sub}</div>',
        unsafe_allow_html=True,
    )


def card(title: str, body: str, tags: list[tuple[str, str]] | None = None):
    """
    渲染一张卡片。
    tags: [(文本, 样式)]，样式取 'default' | 'ok' | 'warn' | 'gray'
    """
    tag_html = ""
    if tags:
        cls_map = {"ok": "zb-tag zb-tag-ok", "warn": "zb-tag zb-tag-warn",
                   "gray": "zb-tag zb-tag-gray", "default": "zb-tag"}
        tag_html = "".join(
            f'<span class="{cls_map.get(style, "zb-tag")}">{text}</span>'
            for text, style in tags
        )
    st.markdown(
        f'<div class="zb-card">'
        f'<div class="zb-card-title">{title}</div>'
        f'<div class="zb-card-body">{body}</div>'
        f'<div style="margin-top:8px">{tag_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def stat_row(items: list[tuple[str, str]]):
    """
    一行统计卡片。items: [(数值, 标签)]，最多建议 4 个。
    """
    if not items:
        return
    cols = st.columns(len(items))
    for col, (num, label) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="zb-stat"><div class="zb-stat-num">{num}</div>'
                f'<div class="zb-stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )


def empty(text: str):
    """空状态提示块。"""
    st.markdown(f'<div class="zb-empty">{text}</div>', unsafe_allow_html=True)


def divider(space: int = 16):
    st.markdown(f'<div style="height:{space}px"></div>', unsafe_allow_html=True)
