# 🐱 知心猫猫 —— 大学生情绪陪伴 AI 助手

> 一只橘色小猫娘形象的 AI 情绪陪伴助手，面向大学生群体。
> 集成 **情绪对话 · 心情追踪 · 危机转介 · 考研咨询 · 408 专业课** 五大功能模块。

- 🌐 **在线体验**：https://zhixin-maomao-jh4sqogd3efrwet7elmkek.streamlit.app/
- 📦 **GitHub**：https://github.com/power1252/zhixin-maomao
- 🏆 **参赛**：第三届"皖智杯"人工智能创新挑战专项赛 → AI 创新设计挑战赛

> 📖 更完整的项目说明（含商业计划要点、TODO、协作约定）见 [PROJECT.md](PROJECT.md)。

---

## ✨ 功能模块

| 模块 | 说明 | 位置 |
|---|---|---|
| ① 情绪陪伴对话 | 橘色小猫娘人设 + 专业共情技巧，开场引导卡片、回复可重生成 | `app.py` + `core/system_prompt.py` |
| ② 情绪识别 + 心情周报 | 自动解析情绪标签落库，分布饼图 + 心情走势曲线，支持 7/14/30 天切换 | `core/emotion_tracker.py` + `pages/📊_心情周报.py` |
| ③ 危机检测 + 自动转介 | 65 词本地词典，命中即返回求助资源，**不调 LLM** | `core/safety.py` + `data/crisis_keywords.txt` |
| ④ 校园场景 RAG | 关键词匹配 20 类大学生真实场景，多话题命中 + 长度加权排序 | `core/campus_rag.py` + `data/campus_faq.json` |
| ⑤ 人格化长期记忆 | SQLite 存最近 10 轮对话，自动塞回 prompt | `core/memory.py` |
| ⑥ 考研咨询 | **137 所**院校库 + 冲/稳/保推荐 + 多维筛选 + 报考建议 + 学习计划 | `core/kaoyan_advisor.py` + `pages/📚_考研咨询.py` |
| ⑦ 408 专业课 | 四科知识地图 + 经典例题 + AI 讲题 + **错题本** | `core/cs408_advisor.py` + `core/wrongbook.py` + `pages/💻_408专业课.py` |
| ⑧ 统一配置 | 密钥三级读取，缺失时优雅降级 | `core/config.py` |
| ⑨ UI 设计系统 | 双主题令牌 + 可复用组件，集中管理全部样式 | `core/theme.py` |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key（三选一）

> ⚠️ 本项目**不允许**把 Key 硬编码进源码。密钥按 `Secrets > 环境变量 > .env` 的优先级读取。

**方式 A：.env 文件（本地开发最省事）**

```bash
cp .env.example .env
# 编辑 .env，填入你在 https://platform.deepseek.com/api_keys 申请的 Key
```

**方式 B：环境变量**

```bash
set LLM_API_KEY=sk-你的key
set LLM_BASE_URL=https://api.deepseek.com
set LLM_MODEL=deepseek-chat
```

**方式 C：Streamlit Secrets（云端部署）**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 填入真实 Key；或直接在 Streamlit Cloud 后台 App settings → Secrets 配置
```

未配置时应用不会崩溃 —— 各页面会显示友好提示，危机检测模块依然正常工作。

### 3. 启动

```bash
streamlit run app.py
# 打开 http://localhost:8501
```

---

## 🗂️ 项目结构

```
emotion-companion/
├── app.py                          # 主入口（聊天页，暖色调）
├── requirements.txt
├── README.md
├── PROJECT.md                      # 项目权威说明书
├── .env.example                    # 环境变量模板
├── .streamlit/
│   └── secrets.toml.example        # Secrets 模板
├── assets/
│   └── cat_avatar.png              # 知心猫猫头像
├── core/
│   ├── theme.py                    # ⑨ 统一 UI 设计系统（双主题+组件）
│   ├── config.py                   # ⑧ 统一配置入口（密钥读取与校验）
│   ├── chat_engine.py              # 对话主流程（串起②③④⑤）
│   ├── system_prompt.py            # 小猫娘人设 + 咨询技巧
│   ├── safety.py                   # ③ 危机检测
│   ├── emotion_tracker.py          # ② 情绪落库
│   ├── campus_rag.py               # ④ 校园 RAG
│   ├── memory.py                   # ⑤ 长期记忆
│   ├── kaoyan_advisor.py           # ⑥ 考研推荐 + 筛选 + 建议 + 计划
│   ├── kaoyan_storage.py           # ⑥ 考研记录落库
│   ├── cs408_advisor.py            # ⑦ 408 讲题
│   └── wrongbook.py                # ⑦ 408 错题本
├── data/
│   ├── campus_faq.json             # 校园话题语料（20 类）
│   ├── crisis_keywords.txt         # 危机关键词词典（65 词）
│   ├── schools.json                # 考研院校库（137 所）
│   ├── cs408_questions.json        # 408 经典例题（12 道）
│   └── *.db                        # 自动生成的 SQLite 库（已 gitignore）
└── pages/
    ├── 📊_心情周报.py
    ├── 📚_考研咨询.py
    └── 💻_408专业课.py
```

---

## 🎨 双主题设计

样式集中在 `core/theme.py`，两个主题令牌（`WARM` / `COOL`）驱动全部页面。

| 页面 | 主题 | 色调 | 风格 |
|---|---|---|---|
| 聊天主页 | `apply_warm()` | 暖米白渐变 + 橘色 `#FF8C5A` | 圆角气泡、柔和阴影、治愈感 |
| 心情周报 | `apply_warm()` | 跟随暖色体系 | 手账感、图表配色和谐化 |
| 考研咨询 | `apply_cool()` | 冷灰白 `#F7F9FC` + 深蓝 `#2C5282` | 卡片式、现代 SaaS |
| 408 专业课 | `apply_cool()` | 冷灰白 + 深蓝 | 卡片网格、进度条、笔记风 |

通用组件：`hero()` 渐变标题条 · `card()` 信息卡 · `stat_row()` 指标卡 · `empty()` 空状态。全局 768px 以下自动适配移动端。

---

## 🧰 技术栈

| 层级 | 选型 |
|---|---|
| 前端 | Streamlit ≥1.30（多页面） |
| 大模型 | DeepSeek-chat（OpenAI 兼容接口） |
| 数据库 | SQLite（mood / memory / kaoyan / wrongbook 四库分离） |
| 可视化 | Plotly |
| 部署 | Streamlit Community Cloud |
| 语言 | Python 3.13 |

---

## ⚠️ 你需要自己配置的东西

1. **`core/safety.py` 中的 `SCHOOL_COUNSELING`** —— 填入本校真实心理咨询中心电话、地址、开放时间。
   留空时系统会自动只展示国家级热线，**不会显示假号码误导用户**。
2. **`.env` / Secrets 中的 API Key** —— 不要提交到仓库。
3. **`data/campus_faq.json` / `data/schools.json`** —— 可按本校情况继续扩充，语料越丰富越准。
