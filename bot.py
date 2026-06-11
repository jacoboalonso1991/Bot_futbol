import os
import asyncio
import requests

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔐 TOKENS
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

CHAT_ID = -1001844013100
seen_events = set()


# =========================
# 🔧 FETCH ASYNC SAFE
# =========================
def fetch(url):
    return requests.get(url, headers=headers, timeout=15).json()


# =========================
# 🏁 START MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("⚽ En vivo", callback_data="live")],
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("📊 Clasificación", callback_data="standings")],
    ]

    await update.message.reply_text(
        "🏆 BOT MUNDIAL ACTIVADO",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# ⚽ LIVE
# =========================
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    data = await asyncio.to_thread(fetch, url)

    matches = data.get("response", [])

    if not matches:
        await query.edit_message_text("⚽ No hay partidos en vivo ahora mismo.")
        return

    msg = "⚽ EN VIVO:\n\n"

    for m in matches[:10]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        g1 = m["goals"]["home"]
        g2 = m["goals"]["away"]
        status = m["fixture"]["status"]["short"]

        msg += f"{home} {g1}-{g2} {away} ({status})\n"

    await query.edit_message_text(msg)


# =========================
# 📅 PARTIDOS HOY (MUNDIAL)
# =========================
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    today_date = datetime.now().strftime("%Y-%m-%d")

    url = f"https://v3.football.api-sports.io/fixtures?date={today_date}"
    data = await asyncio.to_thread(fetch, url)

    matches = data.get("response", [])

    if not matches:
        await query.edit_message_text("📅 No hay partidos hoy.")
        return

    msg = "📅 PARTIDOS HOY:\n\n"

    for m in matches[:15]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        hour = m["fixture"]["date"][11:16]

        msg += f"🕒 {hour} - {home} vs {away}\n"

    await query.edit_message_text(msg[:4000])


# =========================
# 📊 CLASIFICACIÓN MUNDIAL
# =========================
async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/standings?league=1&season=2026"
    data = await asyncio.to_thread(fetch, url)

    response = data.get("response", [])

    if not response:
        await query.edit_message_text("❌ No hay datos de clasificación.")
        return

    groups = response[0]["league"]["standings"]

    msg = "📊 CLASIFICACIÓN MUNDIAL\n\n"

    for group in groups:
        if not group:
            continue

        msg += f"🏆 {group[0]['group']}\n"

        for team in group:
            msg += f"{team['rank']}. {team['team']['name']} ({team['points']} pts)\n"

        msg += "\n"

    await query.edit_message_text(msg[:4000])


# =========================
# 🔀 BOTONES
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = update.callback_query.data

    if data == "live":
        await live(update, context)

    elif data == "today":
        await today(update, context)

    elif data == "standings":
        await standings(update, context)


# =========================
# 🤖 INIT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))


print("🚀 BOT MUNDIAL ONLINE")
app.run_polling()