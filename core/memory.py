"""
⑤ 长期记忆（轻量版）
用 SQLite 存最近 N 轮对话，每次生成回复前把历史塞回 prompt。
不装向量库，靠时间窗口做"短期记忆"。
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "memory.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    return conn

def add_message(role: str, content: str):
    conn = _conn()
    conn.execute(
        "INSERT INTO chat_history (ts, role, content) VALUES (?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), role, content),
    )
    conn.commit()
    conn.close()

def recent_messages(limit: int = 10) -> list[dict]:
    """返回最近 limit 条（role, content），按时间正序。"""
    conn = _conn()
    cur = conn.execute(
        "SELECT role, content FROM (SELECT * FROM chat_history ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
        (limit,),
    )
    rows = [{"role": r[0], "content": r[1]} for r in cur.fetchall()]
    conn.close()
    return rows

def clear_history():
    conn = _conn()
    conn.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
