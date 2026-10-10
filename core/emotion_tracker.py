"""
② 情绪识别 + 长期心情曲线
用 SQLite 存每次对话的情绪标签和时间戳，供"心情周报"页可视化。
情绪标签由LLM在生成回答前顺便输出（见 chat_engine.py）。
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "mood.db"

# 情绪标签枚举（和 prompt 里保持一致）
EMOTIONS = ["joy", "calm", "anxiety", "sadness", "anger", "confusion"]

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            emotion TEXT NOT NULL,
            user_text TEXT,
            ai_reply TEXT
        )
    """)
    return conn

def log_mood(emotion: str, user_text: str, ai_reply: str):
    if emotion not in EMOTIONS:
        emotion = "calm"
    conn = _conn()
    conn.execute(
        "INSERT INTO mood_log (ts, emotion, user_text, ai_reply) VALUES (?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), emotion, user_text, ai_reply),
    )
    conn.commit()
    conn.close()

def fetch_recent(days: int = 7) -> list[dict]:
    conn = _conn()
    cur = conn.execute(
        """SELECT ts, emotion, user_text FROM mood_log
           WHERE ts >= datetime('now', ?)
           ORDER BY ts ASC""",
        (f"-{days} days",),
    )
    rows = [{"ts": r[0], "emotion": r[1], "user_text": r[2]} for r in cur.fetchall()]
    conn.close()
    return rows
