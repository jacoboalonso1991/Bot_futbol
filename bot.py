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

# =========================
# 🔐 CONFIG
# =========================
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

# 🟢 WORLD CUP OPEN DATA (sin key)
WORLD_CUP_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"


# =========================
# 🔧 FETCH
# =========================
def fetch(url):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.json()
    except:
        return {}


def fetch_public(url):
    try:
        r = requests.get(url, timeout=15)
        return r.json()
    except:
        return {}


# =========================
# 🏁 START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("⚽ EN VIVO", callback_data="live")],
        [InlineKeyboardButton("📅 PARTIDOS HOY", callback_data="today")],
        [InlineKeyboardButton("📊 CLASIFICACIÓN", callback_data="standings")],
        [InlineKeyboardButton("🌍 GRUPOS", callback_data="groups")],
    ]

    await update.message.reply_text(
        "🏆 BOT MUNDIAL HÍBRIDO PRO ACTIVADO",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# ⚽ LIVE (API-FOOTBALL)
# =========================
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/fixtures?live=all&league=1&season=2026"
    data = await asyncio.to_thread(fetch, url)

    matches = data.get("response", [])

    if not matches:
        await query.edit_message_text(
            "🔴 EN VIVO\n\n"
            "No hay partidos en directo en este momento ⚽"
        )
        return

    msg = "🔴 EN VIVO MUNDIAL\n\n"

    for m in matches[:10]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        g1 = m["goals"]["home"]
        g2 = m["goals"]["away"]
        status = m["fixture"]["status"]["short"]

        msg += f"{home} {g1}-{g2} {away} ({status})\n"

    await query.edit_message_text(msg)


# =========================
# 📅 PARTIDOS HOY (API-FOOTBALL)
# =========================
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    today_date = datetime.now().strftime("%Y-%m-%d")

    url = f"https://v3.football.api-sports.io/fixtures?league=1&season=2026&date={today_date}"
    data = await asyncio.to_thread(fetch, url)

    matches = data.get("response", [])

    if not matches:
        await query.edit_message_text(
            "📅 PARTIDOS HOY\n\n"
            "No hay partidos programados del Mundial hoy ⚽"
        )
        return

    msg = "📅 PARTIDOS HOY MUNDIAL\n\n"

    for m in matches:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        hour = m["fixture"]["date"][11:16]

        msg += f"🕒 {hour} - {home} vs {away}\n"

    await query.edit_message_text(msg[:4000])


# =========================
# 📊 CLASIFICACIÓN (API-FOOTBALL)
# =========================
async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/standings?league=1&season=2026"
    data = await asyncio.to_thread(fetch, url)

    response = data.get("response", [])

    if not response:
        await query.edit_message_text("❌ No hay clasificación disponible.")
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
# 🌍 GRUPOS (WORLD CUP OPEN DATA FALLBACK)
# =========================
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://raw.githubusercontent.com/openfootball/world-cup/master/2022/worldcup.json"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except:
        await query.edit_message_text(
            "🌍 GRUPOS\n\nNo se pudieron cargar los datos del Mundial."
        )
        return

    rounds = data.get("rounds", [])

    if not rounds:
        await query.edit_message_text(
            "🌍 GRUPOS\n\nDatos no disponibles en este momento."
        )
        return

    msg = "🌍 GRUPOS (BASE)\n\n"

    for r in rounds[:8]:

        name = r.get("name", "Grupo")
        matches = r.get("matches", [])

        msg += f"🏆 {name}\n"

        for m in matches[:4]:
            home = m.get("team1")
            away = m.get("team2")

            if home and away:
                msg += f"{home} vs {away}\n"

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

    elif data == "groups":
        await groups(update, context)


# =========================
# 🤖 INIT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("🚀 BOT MUNDIAL HÍBRIDO PRO ONLINE")
app.run_polling()