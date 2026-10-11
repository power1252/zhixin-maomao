"""
统一配置入口。

配置优先级（从高到低）：
  1. Streamlit Secrets（云端部署推荐）—— st.secrets["LLM_API_KEY"]
  2. 环境变量 —— os.getenv("LLM_API_KEY")
  3. .env 文件（本地开发，可选，需要 python-dotenv）

安全约定：
  - 本项目**禁止**把 API Key 硬编码在源码里。
  - .env 与 .streamlit/secrets.toml 均已在 .gitignore 中，不会进仓库。
  - 如果 Key 缺失，is_configured() 返回 False，各页面会给出友好提示而不是直接崩溃。
"""
import os
from pathlib import Path

# ===== 默认值（非敏感信息可以硬编码）=====
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"

_SECRET_KEYS = ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL")


def _read_dotenv() -> dict[str, str]:
    """读取项目根目录下的 .env（如果存在）。不依赖第三方库，手写极简解析。"""
    env_path = ROOT_DIR / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip().strip('"').strip("'")
    except OSError:
        pass
    return values


def _read_secrets() -> dict[str, str]:
    """读取 Streamlit Secrets（如果运行在 Streamlit 环境下且已配置）。"""
    try:
        import streamlit as st
    except ImportError:
        return {}
    try:
        return {k: st.secrets[k] for k in _SECRET_KEYS if k in st.secrets}
    except Exception:
        # secrets.toml 不存在时 st.secrets 会抛异常，视为未配置
        return {}


_dotenv = _read_dotenv()
_secrets = _read_secrets()


def get(key: str, default: str = "") -> str:
    """按 优先级 Secrets > 环境变量 > .env > default 读取配置项。"""
    if key in _secrets and _secrets[key]:
        return str(_secrets[key])
    env_val = os.getenv(key)
    if env_val:
        return env_val
    if key in _dotenv and _dotenv[key]:
        return _dotenv[key]
    return default


API_KEY = get("LLM_API_KEY")
BASE_URL = get("LLM_BASE_URL", DEFAULT_BASE_URL)
MODEL = get("LLM_MODEL", DEFAULT_MODEL)


def is_configured() -> bool:
    """是否已完成大模型配置（有 Key）。"""
    return bool(API_KEY)


def config_hint() -> str:
    """未配置时给用户的提示文案。"""
    return (
        "⚠️ 还没配置大模型 API Key，猫猫暂时连不上大脑。\n\n"
        "请任选一种方式配置后重启应用：\n"
        "1. **本地开发**：在项目根目录新建 `.env` 文件，写入\n"
        "   `LLM_API_KEY=sk-你的key`\n"
        "2. **Streamlit 云端**：在 Secrets 里配置 `LLM_API_KEY`\n"
        "3. **环境变量**：设置 `LLM_API_KEY`\n\n"
        "推荐使用 DeepSeek（`https://api.deepseek.com`），中文效果好且便宜。"
    )
