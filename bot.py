import os
import io
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import database as db

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID   = os.getenv("CHAT_ID", "")

def only_admin(func):
    """Decorator — отвечает только авторизованному чату."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if CHAT_ID and str(update.effective_chat.id) != str(CHAT_ID):
            await update.message.reply_text("⛔ Нет доступа.")
            return
        return await func(update, ctx)
    return wrapper

# ── /start ────────────────────────────────────────────────────────────────────

@only_admin
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 <b>KOLIZEI — панель управления</b>\n\n"
        "/stats   — статистика отзывов\n"
        "/reviews — последние 5 отзывов\n"
        "/export  — выгрузить все отзывы (CSV)",
        parse_mode="HTML"
    )

# ── /stats ────────────────────────────────────────────────────────────────────

@only_admin
async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = db.get_stats()
    stars = lambda n: "★" * round(float(n)) + "☆" * (5 - round(float(n))) if n != "—" else "—"
    text = (
        "📊 <b>Статистика KOLIZEI</b>\n\n"
        f"📋 Всего отзывов:      <b>{s['total']}</b>\n"
        f"📅 За сегодня:         <b>{s['today']}</b>\n"
        f"📆 За 7 дней:          <b>{s['week']}</b>\n\n"
        f"🖥 Ср. оценка ПК:      <b>{s['avg_pc']}</b>  {stars(s['avg_pc'])}\n"
        f"🤝 Ср. оценка сервиса: <b>{s['avg_svc']}</b>  {stars(s['avg_svc'])}"
    )
    await update.message.reply_text(text, parse_mode="HTML")

# ── /reviews ─────────────────────────────────────────────────────────────────

@only_admin
async def cmd_reviews(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = db.get_recent(5)
    if not rows:
        await update.message.reply_text("Отзывов пока нет.")
        return

    stars = lambda n: ("★" * n + "☆" * (5 - n)) if n else "—"
    lines = ["🗂 <b>Последние отзывы</b>\n"]
    for r in rows:
        lines.append(
            f"<b>#{r['id']}</b> · {r['created_at'][:16]}\n"
            f"👤 {r['name']}  📞 {r['phone']}\n"
            f"🖥 {stars(r['pc_rating'] or 0)}  🤝 {stars(r['svc_rating'] or 0)}\n"
            f"💬 {r['comment'] or '—'}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

# ── /export ───────────────────────────────────────────────────────────────────

@only_admin
async def cmd_export(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    csv_data = db.export_csv()
    if not csv_data.strip():
        await update.message.reply_text("Отзывов пока нет.")
        return
    bio = io.BytesIO(csv_data.encode("utf-8-sig"))
    bio.name = "kolizei_reviews.csv"
    await update.message.reply_document(document=bio, filename="kolizei_reviews.csv",
                                        caption="📁 Все отзывы KOLIZEI")

# ── Main ──────────────────────────────────────────────────────────────────────

def run_bot():
    db.init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("stats",   cmd_stats))
    app.add_handler(CommandHandler("reviews", cmd_reviews))
    app.add_handler(CommandHandler("export",  cmd_export))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
