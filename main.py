import os
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import database as db

app = FastAPI(title="KOLIZEI Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
CHAT_ID     = os.getenv("CHAT_ID", "")

# ── Pydantic schema ──────────────────────────────────────────────────────────

class ReviewIn(BaseModel):
    name:       str
    phone:      str
    pc_rating:  Optional[int] = None
    svc_rating: Optional[int] = None
    comment:    Optional[str] = ""

# ── Telegram helper ──────────────────────────────────────────────────────────

async def tg_send(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }, timeout=8)
        except Exception:
            pass

# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    db.init_db()

# ── Routes ───────────────────────────────────────────────────────────────────

@app.post("/api/reviews")
async def create_review(data: ReviewIn):
    if not data.name.strip() or not data.phone.strip():
        raise HTTPException(400, "name and phone required")

    review_id = db.add_review(
        data.name.strip(), data.phone.strip(),
        data.pc_rating, data.svc_rating,
        data.comment.strip() if data.comment else ""
    )

    stars = lambda n: ("★" * n + "☆" * (5 - n)) if n else "—"
    msg = (
        f"🎮 <b>Новый отзыв #{review_id} — KOLIZEI</b>\n\n"
        f"👤 <b>Имя:</b> {data.name}\n"
        f"📞 <b>Телефон:</b> {data.phone}\n\n"
        f"🖥 <b>ПК/Девайсы:</b>  {stars(data.pc_rating or 0)}  {data.pc_rating or '—'}/5\n"
        f"🤝 <b>Обслуживание:</b> {stars(data.svc_rating or 0)}  {data.svc_rating or '—'}/5\n\n"
        f"💬 <b>Комментарий:</b>\n{data.comment or 'не указан'}"
    )
    asyncio.create_task(tg_send(msg))

    return {"ok": True, "id": review_id}


@app.get("/api/stats")
def get_stats():
    return db.get_stats()


@app.get("/api/reviews")
def get_reviews(limit: int = 10):
    return db.get_recent(limit)


@app.get("/api/export")
def export():
    from fastapi.responses import Response
    csv_data = db.export_csv()
    return Response(
        content=csv_data.encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=kolizei_reviews.csv"}
    )


# ── Serve frontend ────────────────────────────────────────────────────────────

if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
