# 🪵 树洞小室友 —— 大学生情绪陪伴AI对话助手

第三届"皖智杯"人工智能创新挑战专项赛 · 参赛作品骨架

## 已完成的研究方向（对应你选的 ②③④⑤）

| 编号 | 方向 | 实现位置 |
|---|---|---|
| ② | 情绪识别 + 长期心情曲线 | `core/emotion_tracker.py` + `pages/📊_心情周报.py` |
| ③ | 危机检测 + 自动转介 | `core/safety.py` + `data/crisis_keywords.txt` |
| ④ | 校园场景RAG | `core/campus_rag.py` + `data/campus_faq.json` |
| ⑤ | 人格化长期记忆 | `core/memory.py` |

## 快速开始

```bash
# 1. 装依赖
pip install -r requirements.txt

# 2. 填API Key（推荐 DeepSeek，便宜中文好）
#    方式A：设环境变量
set LLM_API_KEY=sk-你的key
set LLM_BASE_URL=https://api.deepseek.com
set LLM_MODEL=deepseek-chat
#    方式B：直接改 core/chat_engine.py 顶部的常量

# 3. 启动
streamlit run app.py
```

## 你需要自己改的东西

1. **`core/safety.py`** 里的 `SCHOOL_COUNSELING`：换成淮南师范学院真实的心理咨询中心电话和地址。
2. **`data/campus_faq.json`**：多加几条你们同学真实会聊的话题（考研、宿舍矛盾、恋爱、就业...），语料越丰富RAG越准。
3. **`data/crisis_keywords.txt`**：按你自己语感补词。

## 项目结构

```
emotion-companion/
├── app.py                    # Streamlit主入口
├── requirements.txt
├── core/
│   ├── chat_engine.py        # 对话主流程（串起②③④⑤）
│   ├── system_prompt.py      # 小室友人设
│   ├── safety.py             # ③ 危机检测
│   ├── emotion_tracker.py    # ② 情绪落库
│   ├── campus_rag.py         # ④ 校园RAG
│   └── memory.py             # ⑤ 长期记忆
├── data/
│   ├── campus_faq.json
│   ├── crisis_keywords.txt
│   ├── mood.db               # 自动生成
│   └── memory.db             # 自动生成
└── pages/
    └── 📊_心情周报.py          # ② 可视化页
```
