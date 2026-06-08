import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔑 CLAVES
TOKEN = "8839239536:AAGs3fI3CTMYTGe6TqLillQNzfSXlUcGvZM"
API_KEY = "97d382767cb1448dac0749cc23009b1a"

headers = {
    "X-Auth-Token": API_KEY
}

# 📊 estado de partidos
last_scores = {}

# 👥 chats activos
chat_ids = set()

# 🏁 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids.add(update.effective_chat.id)
    await update.message.reply_text("🏆 Bot LIVE activado (modo real)")

# 📅 PARTIDOS
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = "https://api.football-data.org/v4/matches"
    data = requests.get(url, headers=headers).json()

    matches = data.get("matches", [])

    msg = "📅 PARTIDOS:\n\n"

    for m in matches[:10]:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        status = m["status"]

        msg += f"{home} vs {away} - {status}\n"

    await update.message.reply_text(msg)

# 📊 CLASIFICACIÓN
async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = "https://api.football-data.org/v4/competitions/WC/standings"
    data = requests.get(url, headers=headers).json()

    standings = data.get("standings", [])

    msg = "📊 CLASIFICACIÓN:\n\n"

    for group in standings:
        name = group.get("group", "GENERAL")
        msg += f"\n🏆 {name}\n"

        for team in group["table"]:
            msg += f"{team['position']}. {team['team']['name']} - {team['points']} pts\n"

    await update.message.reply_text(msg)

# 🌍 GRUPOS
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = "https://api.football-data.org/v4/competitions/WC/standings"
    data = requests.get(url, headers=headers).json()

    standings = data.get("standings", [])

    msg = "🌍 GRUPOS DEL MUNDIAL:\n\n"

    for group in standings:
        name = group.get("group", "GENERAL")
        msg += f"\n🏟️ {name}\n"

        for team in group["table"]:
            msg += f"- {team['team']['name']}\n"

    await update.message.reply_text(msg)

# 🔥 LIVE REAL CHECKER
async def live_checker(app):
    global last_scores

    while True:
        try:

            url = "https://api.football-data.org/v4/matches"
            data = requests.get(url, headers=headers).json()

            matches = data.get("matches", [])

            for m in matches:

                status = m["status"]

                if status not in ["LIVE", "IN_PLAY", "PAUSED", "FINISHED"]:
                    continue

                match_id = m["id"]
                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                home_score = m["score"]["fullTime"]["home"] or 0
                away_score = m["score"]["fullTime"]["away"] or 0

                new_state = f"{home_score}-{away_score}"
                old_state = last_scores.get(match_id)

                if old_state != new_state:
                    last_scores[match_id] = new_state

                    text = f"⚽ GOL!\n{home} {new_state} {away}"

                    for chat_id in chat_ids:
                        await app.bot.send_message(chat_id=chat_id, text=text)

        except Exception as e:
            print("Error live:", e)

        await asyncio.sleep(30)

# 🤖 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("standings", standings))
app.add_handler(CommandHandler("groups", groups))

# 🚀 iniciar loop
async def post_init(app):
    asyncio.create_task(live_checker(app))

app.post_init = post_init

print("Bot LIVE en marcha...")
app.run_polling()