"""
408 错题本存储层
独立建表（不碰现有库），遵循 PROJECT.md「数据库改动向后兼容」约定。
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "wrongbook.db"

# 常见错因分类（下拉选项）
ERROR_REASONS = [
    "概念不清",
    "计算失误",
    "审题不仔细",
    "知识点遗忘",
    "思路错误",
    "时间不够",
    "其他",
]


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wrong_question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT,
            question TEXT NOT NULL,
            my_answer TEXT,
            answer TEXT,
            analysis TEXT,
            reason TEXT,
            note TEXT,
            source TEXT,
            mastered INTEGER DEFAULT 0
        )
    """)
    return conn


def add_wrong(
    subject: str,
    question: str,
    topic: str = "",
    my_answer: str = "",
    answer: str = "",
    analysis: str = "",
    reason: str = "",
    note: str = "",
    source: str = "手动录入",
) -> int:
    """新增一条错题，返回自增 id。"""
    conn = _conn()
    cur = conn.execute(
        """INSERT INTO wrong_question
           (ts, subject, topic, question, my_answer, answer, analysis, reason, note, source, mastered)
           VALUES (?,?,?,?,?,?,?,?,?,?,0)""",
        (
            datetime.now().isoformat(timespec="seconds"),
            subject, topic, question, my_answer, answer,
            analysis, reason, note, source,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def exists(subject: str, question: str) -> bool:
    """判断同一道题是否已在错题本中（避免重复加入）。"""
    conn = _conn()
    cur = conn.execute(
        "SELECT 1 FROM wrong_question WHERE subject=? AND question=? LIMIT 1",
        (subject, question),
    )
    found = cur.fetchone() is not None
    conn.close()
    return found


def list_wrong(subject: str | None = None, only_unmastered: bool = False) -> list[dict]:
    """查询错题列表，支持按科目筛选、只看未掌握。"""
    sql = "SELECT * FROM wrong_question WHERE 1=1"
    params: list = []
    if subject and subject != "全部":
        sql += " AND subject=?"
        params.append(subject)
    if only_unmastered:
        sql += " AND mastered=0"
    sql += " ORDER BY id DESC"

    conn = _conn()
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def set_mastered(qid: int, mastered: bool = True):
    """标记为已掌握 / 取消掌握。"""
    conn = _conn()
    conn.execute(
        "UPDATE wrong_question SET mastered=? WHERE id=?",
        (1 if mastered else 0, qid),
    )
    conn.commit()
    conn.close()


def update_note(qid: int, reason: str = "", note: str = ""):
    """更新错因与备注（复习后补充心得）。"""
    conn = _conn()
    conn.execute(
        "UPDATE wrong_question SET reason=?, note=? WHERE id=?",
        (reason, note, qid),
    )
    conn.commit()
    conn.close()


def delete_wrong(qid: int):
    conn = _conn()
    conn.execute("DELETE FROM wrong_question WHERE id=?", (qid,))
    conn.commit()
    conn.close()


def stats() -> dict:
    """错题统计：总数、已掌握、各科目分布。"""
    conn = _conn()
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) AS c FROM wrong_question").fetchone()["c"]
    mastered = conn.execute(
        "SELECT COUNT(*) AS c FROM wrong_question WHERE mastered=1"
    ).fetchone()["c"]
    by_subject = [
        dict(r)
        for r in conn.execute(
            """SELECT subject,
                      COUNT(*) AS total,
                      SUM(mastered) AS done
               FROM wrong_question GROUP BY subject ORDER BY total DESC"""
        ).fetchall()
    ]
    conn.close()
    return {
        "total": total,
        "mastered": mastered,
        "unmastered": total - mastered,
        "by_subject": by_subject,
    }
