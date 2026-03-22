import sqlite3
import csv
import io
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = "kolizei.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                phone     TEXT    NOT NULL,
                pc_rating INTEGER,
                svc_rating INTEGER,
                comment   TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

def add_review(name, phone, pc_rating, svc_rating, comment):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reviews (name,phone,pc_rating,svc_rating,comment) VALUES (?,?,?,?,?)",
            (name, phone, pc_rating, svc_rating, comment)
        )
        return cur.lastrowid

def get_recent(limit=5):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reviews ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE date(created_at)=date('now','localtime')"
        ).fetchone()[0]
        week = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE created_at >= datetime('now','-7 days','localtime')"
        ).fetchone()[0]
        avgs = conn.execute(
            "SELECT ROUND(AVG(pc_rating),1), ROUND(AVG(svc_rating),1) FROM reviews WHERE pc_rating IS NOT NULL"
        ).fetchone()
    return {
        "total": total,
        "today": today,
        "week": week,
        "avg_pc": avgs[0] or "—",
        "avg_svc": avgs[1] or "—",
    }

def export_csv():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Имя","Телефон","ПК/Девайсы","Обслуживание","Комментарий","Дата"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["phone"],
                         r["pc_rating"], r["svc_rating"], r["comment"], r["created_at"]])
    return output.getvalue()
