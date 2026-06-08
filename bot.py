import requests
import os
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {"X-Auth-Token": API_KEY}

# 👉 PON AQUÍ TU ID DE GRUPO
CHAT_ID = -1001234567890


# 🏆 MENÚ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")]
    ]

    await update.message.reply_text(
        "🚀 MUNDIAL LIVE ACTIVADO",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📅 PARTIDOS
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://api.football-data.org/v4/matches"
    data = requests.get(url, headers=headers).json()

    matches = data.get("matches", [])

    msg = "📅 PARTIDOS:\n\n"

    for m in matches[:10]:
        msg += f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} - {m['status']}\n"

    await query.edit_message_text(msg)


# 🌍 GRUPOS (simple)
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Grupo A", callback_data="a")],
        [InlineKeyboardButton("Grupo B", callback_data="b")]
    ]

    await query.edit_message_text(
        "Selecciona grupo (demo)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔥 LIVE WATCHER
async def live_checker(app):

    last_state = {}

    while True:

        try:
            url = "https://api.football-data.org/v4/matches"
            data = requests.get(url, headers=headers).json()

            matches = data.get("matches", [])

            for m in matches:

                match_id = m["id"]
                status = m["status"]
                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                # 🔴 INICIO PARTIDO
                if status == "IN_PLAY" and last_state.get(match_id) != "IN_PLAY":

                    await app.bot.send_message(
                        CHAT_ID,
                        f"⚽ INICIO PARTIDO\n{home} vs {away}"
                    )

                # 🏁 FINAL
                if status == "FINISHED" and last_state.get(match_id) != "FINISHED":

                    await app.bot.send_message(
                        CHAT_ID,
                        f"🏁 FINAL DEL PARTIDO\n{home} vs {away}"
                    )

                last_state[match_id] = status

        except Exception as e:
            print("Error live checker:", e)

        await asyncio.sleep(60)


# 🔀 BOTONES
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    if data == "today":
        await today(update, context)

    elif data == "groups":
        await groups(update, context)


# 🤖 MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))


# 🚀 ARRANCAR BOT + LIVE SYSTEM
async def post_init(app):
    asyncio.create_task(live_checker(app))


app.post_init = post_init

print("BOT LIVE CON AVISOS ACTIVADO 🚀")
app.run_polling()