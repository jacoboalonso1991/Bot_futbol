import requests
import os
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# 🔐 ENV
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {"x-apisports-key": API_KEY}

# 🧠 CONFIG
CHAT_ID = -1001844013100
seen_events = set()


# 🆔 CHAT ID
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🆔 CHAT ID:\n{chat_id}")


# 🏆 START MENU PRO
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("⚽ En vivo", callback_data="live")],
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")],
        [InlineKeyboardButton("📊 Clasificación", callback_data="standings")],
        [InlineKeyboardButton("🆔 CHAT ID", callback_data="id")]
    ]

    await update.message.reply_text(
        "🏆 BOT MUNDIAL PRO ACTIVADO",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ⚽ LIVE
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    data = requests.get(url, headers=headers).json()

    matches = data.get("response", [])

    msg = "⚽ EN VIVO:\n\n"

    for m in matches[:10]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        g1 = m["goals"]["home"]
        g2 = m["goals"]["away"]
        status = m["fixture"]["status"]["short"]

        msg += f"{home} {g1}-{g2} {away} ({status})\n"

    await query.edit_message_text(msg)


# 📅 PARTIDOS HOY
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = requests.get(
        "https://v3.football.api-sports.io/fixtures?live=all",
        headers=headers
    ).json()

    matches = data.get("response", [])

    msg = "📅 PARTIDOS:\n\n"

    for m in matches[:10]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        msg += f"{home} vs {away}\n"

    await query.edit_message_text(msg)


# 🌍 GRUPOS (REALES POR COMPETICIÓN)
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Grupo A", callback_data="group_A"),
         InlineKeyboardButton("Grupo B", callback_data="group_B")],
        [InlineKeyboardButton("Grupo C", callback_data="group_C"),
         InlineKeyboardButton("Grupo D", callback_data="group_D")],
        [InlineKeyboardButton("Grupo E", callback_data="group_E"),
         InlineKeyboardButton("Grupo F", callback_data="group_F")],
        [InlineKeyboardButton("Grupo G", callback_data="group_G"),
         InlineKeyboardButton("Grupo H", callback_data="group_H")]
    ]

    await query.edit_message_text(
        "🌍 Selecciona grupo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📊 CLASIFICACIÓN REAL
async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/standings?league=1&season=2024"
    data = requests.get(url, headers=headers).json()

    response = data.get("response", [])

    msg = "📊 CLASIFICACIÓN:\n\n"

    if response:
        tables = response[0]["league"]["standings"][0]

        for team in tables[:10]:
            name = team["team"]["name"]
            points = team["points"]
            msg += f"{team['rank']}. {name} - {points} pts\n"

    await query.edit_message_text(msg)


# 🔥 LIVE ENGINE
async def live_checker(app):

    global seen_events

    while True:

        try:
            data = requests.get(
                "https://v3.football.api-sports.io/fixtures?live=all",
                headers=headers
            ).json()

            matches = data.get("response", [])

            for m in matches:

                fixture_id = m["fixture"]["id"]
                home = m["teams"]["home"]["name"]
                away = m["teams"]["away"]["name"]

                goals_h = m["goals"]["home"]
                goals_a = m["goals"]["away"]

                events = m.get("events", [])

                for e in events:

                    player = e.get("player", {}).get("name", "Desconocido")
                    minute = e.get("time", {}).get("elapsed", 0)
                    etype = e.get("type", "")
                    detail = e.get("detail", "")

                    event_id = f"{fixture_id}-{etype}-{player}-{minute}"

                    if event_id in seen_events:
                        continue

                    seen_events.add(event_id)

                    # ⚽ GOL
                    if etype == "Goal":

                        if CHAT_ID:
                            await app.bot.send_message(
                                CHAT_ID,
                                f"⚽ GOOOOOOL!\n{home} {goals_h}-{goals_a} {away}\n🎯 {player} ({minute}')"
                            )

                    # 🟥 ROJA
                    elif etype == "Card" and detail == "Red Card":

                        if CHAT_ID:
                            await app.bot.send_message(
                                CHAT_ID,
                                f"🟥 EXPULSIÓN!\n{home} vs {away}\n❌ {player} ({minute}')"
                            )

        except Exception as e:
            print("LIVE ERROR:", e)

        await asyncio.sleep(30)


# 🔀 BOTONES
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = update.callback_query.data

    if data == "live":
        await live(update, context)

    elif data == "today":
        await today(update, context)

    elif data == "groups":
        await groups(update, context)

    elif data == "standings":
        await standings(update, context)

    elif data == "id":
        await get_id(update, context)


# 🤖 BOT INIT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", get_id))
app.add_handler(CallbackQueryHandler(buttons))


# 🚀 LIVE SYSTEM
async def post_init(app):
    asyncio.create_task(live_checker(app))

app.post_init = post_init

print("🚀 BOT MUNDIAL PRO A ACTIVADO")
app.run_polling()