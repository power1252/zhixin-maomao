"""
408 闯关小游戏 · 进度存储层

独立建表（不碰现有库），遵循 PROJECT.md「数据库改动向后兼容」约定。
关卡与 cs408_advisor.SUBJECTS 一一对应，按科目顺序逐关解锁。
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "game_progress.db"

# 每关满星，用于总进度换算
STARS_PER_LEVEL = 3


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS game_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            subject TEXT NOT NULL,
            total_q INTEGER NOT NULL,
            correct_q INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            accuracy REAL NOT NULL
        )
    """)
    return conn


def record_play(subject: str, total_q: int, correct_q: int, stars: int):
    """记录一次通关结果。accuracy 由 正确/总数 计算，保留 4 位。"""
    accuracy = round(correct_q / total_q, 4) if total_q else 0.0
    conn = _conn()
    conn.execute(
        "INSERT INTO game_record (ts, subject, total_q, correct_q, stars, accuracy) "
        "VALUES (?,?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), subject,
         total_q, correct_q, stars, accuracy),
    )
    conn.commit()
    conn.close()


def best_stars(subject: str) -> int:
    """某科目历史最好星级（0~3）。未玩过返回 0。"""
    conn = _conn()
    row = conn.execute(
        "SELECT MAX(stars) FROM game_record WHERE subject=?", (subject,)
    ).fetchone()
    conn.close()
    return int(row[0]) if row and row[0] is not None else 0


def subject_stats() -> dict:
    """各科目累计统计：总题数、正确数、最好星级、游玩次数。以 subject 为键。"""
    conn = _conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT subject,
                  COALESCE(SUM(total_q),0)   AS total,
                  COALESCE(SUM(correct_q),0) AS correct,
                  COALESCE(MAX(stars),0)     AS best_stars,
                  COUNT(*)                   AS plays
           FROM game_record GROUP BY subject"""
    ).fetchall()
    conn.close()
    return {r["subject"]: dict(r) for r in rows}


def overall() -> dict:
    """全局统计：累计答题数、累计正确数、游玩次数、已挑战科目数、累计星数(最好星级求和)。"""
    conn = _conn()
    row = conn.execute(
        """SELECT COALESCE(SUM(total_q),0)   AS total,
                  COALESCE(SUM(correct_q),0) AS correct,
                  COUNT(*)                   AS plays
           FROM game_record"""
    ).fetchone()
    conn.close()
    stats = subject_stats()
    subjects_played = len(stats)
    total_stars = sum(s["best_stars"] for s in stats.values())
    total_q = int(row["total"]) if row else 0
    correct_q = int(row["correct"]) if row else 0
    return {
        "total_q": total_q,
        "correct_q": correct_q,
        "plays": int(row["plays"]) if row else 0,
        "subjects_played": subjects_played,
        "total_stars": total_stars,
    }


def is_unlocked(subject: str, subjects_order: list[str]) -> bool:
    """关卡解锁规则：第一关默认解锁；其余关需前一关最好星级 ≥ 1（即通过）。"""
    if subject not in subjects_order:
        return False
    idx = subjects_order.index(subject)
    if idx == 0:
        return True
    prev = subjects_order[idx - 1]
    return best_stars(prev) >= 1


def stars_for_accuracy(correct: int, total: int) -> int:
    """根据正确率换算星级：≥90%→3，≥70%→2，≥50%→1，否则 0。"""
    if total == 0:
        return 0
    rate = correct / total
    if rate >= 0.9:
        return 3
    if rate >= 0.7:
        return 2
    if rate >= 0.5:
        return 1
    return 0
