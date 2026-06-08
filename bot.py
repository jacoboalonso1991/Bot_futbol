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

# 🔐 ENV
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

# 📡 HEADERS API-FOOTBALL
headers = {
    "x-apisports-key": API_KEY
}

# 🧠 ID DEL GRUPO (lo pones luego con /id)
CHAT_ID = None

# 🧾 EVITAR DUPLICADOS
seen_events = set()


# 🆔 SACAR CHAT ID
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🆔 CHAT ID: {chat_id}")


# 🏆 START MENU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")],
        [InlineKeyboardButton("🆔 CHAT ID", callback_data="id")]
    ]

    await update.message.reply_text(
        "🚀 BOT FÚTBOL LIVE ACTIVADO",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📅 PARTIDOS
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    data = requests.get(url, headers=headers).json()

    response = data.get("response", [])

    msg = "📅 PARTIDOS EN DIRECTO:\n\n"

    for match in response[:10]:

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        status = match["fixture"]["status"]["short"]

        msg += f"{home} vs {away} - {status}\n"

    await query.edit_message_text(msg)


# 🌍 GRUPOS (demo simple)
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Grupo A", callback_data="a")],
        [InlineKeyboardButton("Grupo B", callback_data="b")]
    ]

    await query.edit_message_text(
        "Selecciona grupo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔥 LIVE ENGINE (GOLES + ROJAS REALES)
async def live_checker(app):

    global seen_events

    while True:

        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"

            data = requests.get(url, headers=headers).json()
            response = data.get("response", [])

            for match in response:

                fixture_id = match["fixture"]["id"]
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]

                events = match.get("events", [])

                for event in events:

                    player = event.get("player", {}).get("name", "Desconocido")
                    minute = event.get("time", {}).get("elapsed", 0)
                    event_type = event.get("type", "")
                    detail = event.get("detail", "")

                    event_id = f"{fixture_id}-{minute}-{event_type}-{player}"

                    if event_id in seen_events:
                        continue

                    seen_events.add(event_id)

                    # ⚽ GOL
                    if event_type == "Goal":

                        if CHAT_ID:
                            await app.bot.send_message(
                                CHAT_ID,
                                f"⚽ GOOOOOOL!\n{home} vs {away}\n🎯 {player} ({minute}')"
                            )

                    # 🟥 ROJA
                    elif event_type == "Card" and detail == "Red Card":

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

    if data == "today":
        await today(update, context)

    elif data == "groups":
        await groups(update, context)

    elif data == "id":
        await get_id(update, context)


# 🤖 MAIN BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", get_id))
app.add_handler(CallbackQueryHandler(buttons))


# 🚀 LIVE SYSTEM
async def post_init(app):
    asyncio.create_task(live_checker(app))


app.post_init = post_init

print("🚀 BOT LIVE CON API-FOOTBALL ACTIVADO")
app.run_polling()