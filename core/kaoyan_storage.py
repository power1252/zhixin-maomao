"""
考研咨询记录落库
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "kaoyan.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kaoyan_recommend (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            user_school TEXT,
            user_major TEXT,
            score_level TEXT,
            region TEXT,
            reason TEXT,
            weakness TEXT,
            chong TEXT,
            wen TEXT,
            bao TEXT,
            advice TEXT
        )
    """)
    return conn

def save_recommendation(profile: dict, rec: dict, advice: str):
    conn = _conn()
    conn.execute(
        """INSERT INTO kaoyan_recommend
           (ts, user_school, user_major, score_level, region, reason, weakness, chong, wen, bao, advice)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.now().isoformat(timespec="seconds"),
            profile.get("school", ""), profile.get("major", ""),
            profile.get("score", ""), profile.get("region", ""),
            profile.get("reason", ""), profile.get("weakness", ""),
            json.dumps(rec.get("chong", []), ensure_ascii=False),
            json.dumps(rec.get("wen", []), ensure_ascii=False),
            json.dumps(rec.get("bao", []), ensure_ascii=False),
            advice,
        ),
    )
    conn.commit()
    conn.close()

def fetch_history(limit: int = 20) -> list[dict]:
    conn = _conn()
    cur = conn.execute(
        """SELECT id, ts, user_school, user_major, score_level, region, chong, wen, bao, advice
           FROM kaoyan_recommend ORDER BY id DESC LIMIT ?""",
        (limit,),
    )
    rows = []
    for r in cur.fetchall():
        rows.append({
            "id": r[0], "ts": r[1], "school": r[2], "major": r[3],
            "score": r[4], "region": r[5],
            "chong": json.loads(r[6] or "[]"),
            "wen": json.loads(r[7] or "[]"),
            "bao": json.loads(r[8] or "[]"),
            "advice": r[9],
        })
    conn.close()
    return rows
