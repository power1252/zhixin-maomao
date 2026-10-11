# 知心猫猫 · 项目说明书

> 本文档为项目权威说明，AI 协作工具（WorkBuddy / Copilot 等）可直接读取并在此基础上继续编辑、扩展。
> 最后更新：2026-10-11

---

## 一、项目一句话介绍

**"知心猫猫"** 是一只橘色小猫娘形象的 AI 情绪陪伴助手，面向大学生群体，集成情绪对话、心情追踪、危机转介、考研咨询、408 专业课学习五大功能模块，基于 Streamlit + DeepSeek 大模型搭建，已部署上线。

- **在线访问**：https://zhixin-maomao-jh4sqogd3efrwet7elmkek.streamlit.app/
- **GitHub 仓库**：https://github.com/power1252/zhixin-maomao
- **作者**：杨国富（淮南师范学院 软件工程）
- **参赛方向**：第三届"皖智杯"人工智能创新挑战专项赛 → **AI 创新设计挑战赛**
- **后续规划**：2027 年"挑战杯"小挑（创业计划竞赛）

---

## 二、技术栈

| 层级 | 选型 | 版本/说明 |
|---|---|---|
| 前端 | Streamlit | ≥1.30，多页面结构 |
| 大模型 | DeepSeek-chat | OpenAI 兼容接口，temperature=0.85 |
| 数据库 | SQLite | 本地文件，三库分离 |
| 可视化 | Plotly | 心情周报饼图/折线图 |
| 部署 | Streamlit Community Cloud | 免费公网托管 |
| 版本控制 | Git + GitHub | main 分支自动部署 |
| 语言 | Python 3.13 | |

---

## 三、功能模块清单

### 模块 ① 情绪陪伴对话（主页 app.py）
- 橘色小猫娘人设（带猫耳、尾巴、软萌口癖）
- 专业咨询技巧：情感反映、内容反映、开放式提问、附和式倾听、正常化、温柔挑战
- 强制短回复（≤80字）、温度 0.85、禁止 AI 腔
- 输出格式：`EMOTION: <标签>` + `REPLY: <内容>`
- 情绪标签 6 类：joy / calm / anxiety / sadness / anger / confusion

### 模块 ② 情绪识别 + 心情曲线（pages/📊_心情周报.py）
- 每轮对话自动解析情绪标签，落 SQLite
- 饼图：本周情绪分布
- 折线图：每日情绪趋势
- 表格：最近 10 条对话回顾

### 模块 ③ 危机检测 + 自动转介（core/safety.py）
- 本地关键词词典（18 个危机词：自杀、不想活、自残…）
- 命中即返回安全话术 + 校心理咨询中心联系方式
- **最高优先级**：不调 LLM，直接返回

### 模块 ④ 校园场景 RAG（core/campus_rag.py）
- 轻量关键词匹配（无向量库）
- 5 类话题：学业焦虑 / 失恋 / 宿舍人际 / 就业 / 家庭经济
- 命中后把参考话术塞给 LLM，引导其更贴近大学生语境

### 模块 ⑤ 长期记忆（core/memory.py）
- SQLite 存最近 10 轮对话
- 每次对话前自动塞回 prompt
- 侧边栏可一键清空

### 模块 ⑥ 考研咨询（pages/📚_考研咨询.py）
- 院校库：137 所代表性院校（985 / 211 / 双非分层，覆盖 31 个省份，含安徽本地 12 所）
- 字段：院校名 / 层次 / 省份 / 城市 / 学科评估等级 / 难度 1-5 / 参考分数 / 是否接收调剂 / 备注
- 三档推荐：冲 / 稳 / 保
- 筛选维度：地区、层次、难度、只看接收调剂、院校名关键词
- LLM 生成个性化报考建议 + 按月学习计划
- 历史推荐记录落 SQLite（core/kaoyan_storage.py）

### 模块 ⑦ 408 专业课学习（pages/💻_408专业课.py）
- 四科知识地图：数据结构 / 计组 / OS / 数据库（卡片式）
- 12 道经典例题（带详细解析）
- AI 讲题：贴题自动按"考点→思路→答案→易错点→举一反三"五段式讲解
- **错题本**：例题可一键加入、记录错因与笔记、掌握状态标记、各科目掌握率进度条（core/wrongbook.py）

### 模块 ⑧ 统一配置管理（core/config.py）
- 密钥读取优先级：Streamlit Secrets > 环境变量 > .env > 默认值
- **禁止硬编码 API Key**；缺失时降级为友好提示而非崩溃
- 提供 `.env.example` 与 `.streamlit/secrets.toml.example` 模板

### 模块 ⑨ 统一 UI 设计系统（core/theme.py）
- 两套主题令牌：`WARM` 治愈暖色（聊天页 / 心情周报）、`COOL` 现代 SaaS 冷色（考研 / 408）
- 集中管理配色、字体层级、圆角体系、阴影规范、组件样式
- 可复用组件：`hero()` 渐变标题条、`card()` 信息卡、`stat_row()` 指标卡、`empty()` 空状态
- 全局响应式：768px 以下自动收缩留白与字号
- **改配色只需动 theme.py 里的令牌字典，不用翻各页面**

---

## 四、代码结构

```
emotion-companion/
├── app.py                          # 主入口（聊天页，暖色调）
├── requirements.txt
├── README.md
├── PROJECT.md                      # ← 本文档
├── .streamlit/
│   └── config.toml                 # 全局主题配置
├── assets/
│   └── cat_avatar.png             # 知心猫猫头像（AI生成）
├── core/
│   ├── __init__.py
│   ├── theme.py                     # ⑨ 统一 UI 设计系统（双主题令牌+组件）
│   ├── config.py                    # ⑧ 统一配置（密钥读取/校验）
│   ├── chat_engine.py              # 对话主流程（串起②③④⑤）
│   ├── system_prompt.py             # 小猫娘人设 + 咨询技巧
│   ├── safety.py                  # ③ 危机检测
│   ├── emotion_tracker.py         # ② 情绪落库
│   ├── campus_rag.py               # ④ 校园RAG
│   ├── memory.py                   # ⑤ 长期记忆
│   ├── kaoyan_advisor.py           # ⑥ 考研推荐+筛选+建议+计划
│   ├── kaoyan_storage.py           # ⑥ 考研记录落库
│   ├── cs408_advisor.py            # ⑦ 408讲题
│   └── wrongbook.py                 # ⑦ 408错题本
├── data/
│   ├── campus_faq.json             # 校园话题语料（20 类）
│   ├── crisis_keywords.txt         # 危机关键词词典（65 词）
│   ├── schools.json                 # 考研院校库（137所，含地区/学科/调剂字段）
│   ├── cs408_questions.json         # 408经典例题（12道）
│   └── *.db                         # 自动生成的 SQLite 库
└── pages/
    ├── 📊_心情周报.py
    ├── 📚_考研咨询.py
    └── 💻_408专业课.py
```

---

## 五、双主题设计（UI 规范）

> 样式统一由 `core/theme.py` 注入，改配色只动那里的令牌字典。

| 页面 | 主题函数 | 色调 | 风格 |
|---|---|---|---|
| 聊天主页 | `theme.apply_warm()` | 暖米白渐变 + 橘色 `#FF8C5A` | 圆角气泡、柔和阴影、治愈感 |
| 心情周报 | `theme.apply_warm()` | 跟随暖色体系 | 手账感、图表配色和谐化 |
| 考研咨询 | `theme.apply_cool()` | 冷灰白 `#F7F9FC` + 深蓝 `#2C5282` | 卡片式、现代 SaaS |
| 408 专业课 | `theme.apply_cool()` | 冷灰白 + 深蓝 | 卡片网格、进度条、笔记风 |

通用组件：`hero()` 渐变标题条 / `card()` 信息卡 / `stat_row()` 指标卡 / `empty()` 空状态。

---

## 六、配置说明（Secrets）

> ⚠️ **绝对不要**把 API Key 写进源码。密钥按 `Streamlit Secrets > 环境变量 > .env` 优先级读取。

云端请在 Streamlit Cloud 的 App settings → Secrets 中配置：

```toml
LLM_API_KEY = "sk-你的key"
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"
```

本地开发复制模板即可：

```bash
cp .env.example .env
# 或
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Key 申请地址：https://platform.deepseek.com/api_keys

未配置时应用不会崩溃：聊天页会显示配置指引，危机检测模块照常工作。

---

## 七、本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 Key
cp .env.example .env   # 然后编辑 .env 填入真实 Key

# 启动
streamlit run app.py
# 默认 http://localhost:8501
```

---

## 八、部署流程（已完成）

1. 代码推送到 GitHub：`power1252/zhixin-maomao`
2. 登录 share.streamlit.io
3. 选择仓库 → main 分支 → 主文件 app.py
4. 配置上述 Secrets
5. Deploy，自动获得 `*.streamlit.app` 域名
6. 之后本地 `git push` 即自动重新部署

---

## 九、待改进 / TODO（按优先级）

- [x] **【高】** ~~把 `core/safety.py` 里的 `SCHOOL_COUNSELING` 换成真实信息~~ → 已改为留空自动降级，只展示真实热线（待你填入本校信息）
- [x] **【高】** ~~扩充 `data/schools.json` 院校库到 50+ 所~~ → 已扩至 137 所，含地区/学科等级/调剂字段
- [x] **【中】** ~~扩充 `data/campus_faq.json` 到 15~20 个话题~~ → 已扩至 20 类
- [x] **【中】** ~~408 模块加入错题本功能~~ → 已完成（core/wrongbook.py）
- [x] **【高】** ~~移除硬编码 API Key~~ → 已迁至 core/config.py，支持 Secrets/环境变量/.env
- [x] **【中】** ~~UI 优化~~ → 已完成，四个页面统一设计系统（core/theme.py）
- [ ] **【高】** 去 DeepSeek 后台吊销旧的已泄露 Key（`sk-1b25...c3e2`）
- [ ] **【中】** 用户注册/登录（当前匿名）
- [ ] **【低】** 语音输入输出
- [ ] **【低】** 接入向量数据库（Chroma）替代关键词 RAG
- [ ] **【低】** 移动端适配优化（已做基础响应式，可进一步打磨）

---

## 十、比赛申报信息

### 已报名
- **赛事**：第三届"皖智杯"安徽省青少年智能创新公开赛
- **赛道**：人工智能创新挑战专项赛 → AI 创新设计挑战赛
- **报名网址**：https://ai.qsnkjjs.org.cn
- **报名截止**：2026-10-31
- **学校统计表**：https://www.kdocs.cn/l/cgdaQfDxxcV2

### 商业计划书要点（挑战杯小挑备用）
- 痛点：大学生心理求助率约 20%，校心理咨询排队 2 周
- 解决方案：7×24 AI 陪伴 + 危机自动转介
- 差异化：校园场景垂直化 + 学业辅助（考研/408）一体化
- 目标用户：安徽省内高校大学生
- 盈利模式（待定）：B 端卖给高校心理中心 / C 端会员增值

---

## 十一、AI 协作工具编辑指南

如果是 WorkBuddy / Copilot 等 AI 工具读取本文档继续开发，请遵循：

1. **不要改人设核心**：小猫娘 + 专业共情技巧是产品灵魂，不要改成冷冰冰的客服
2. **不要删危机检测模块**：这是社会价值核心，任何改动必须保留 safety.py 最高优先级
3. **新功能请新建文件**：不要污染现有模块，按 `core/xxx.py` + `pages/xxx.py` 模式扩展
4. **数据库改动向后兼容**：新增字段用 ALTER TABLE，不要重建表
5. **Secrets 不要硬编码进 git**：必须走 core/config.py 的统一入口（Secrets / 环境变量 / .env）
6. **提交前跑语法检查**：`python -m py_compile <改动文件>`
7. **UI 保持双主题**：聊天类暖色、学习类冷色
