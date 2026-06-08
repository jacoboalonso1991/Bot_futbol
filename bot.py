import requests
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# 🔐 VARIABLES DE ENTORNO (Railway)
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {"X-Auth-Token": API_KEY}


# 🏆 MENÚ PRINCIPAL
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")],
        [InlineKeyboardButton("📊 Clasificación", callback_data="standings")]
    ]

    await update.message.reply_text(
        "🚀 MUNDIAL 2026",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📅 PARTIDOS HOY
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://api.football-data.org/v4/matches"
    data = requests.get(url, headers=headers).json()

    matches = data.get("matches", [])

    if not matches:
        await query.edit_message_text("⚽ No hay partidos disponibles.")
        return

    msg = "📅 PARTIDOS HOY:\n\n"

    for m in matches[:10]:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        status = m["status"]

        msg += f"{home} vs {away} - {status}\n"

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver", callback_data="back")]
    ]

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


# 🌍 GRUPOS (MANUALES)
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
         InlineKeyboardButton("Grupo H", callback_data="group_H")],

        [InlineKeyboardButton("⬅️ Volver", callback_data="back")]
    ]

    await query.edit_message_text(
        "🌍 Selecciona un grupo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📊 DETALLE DE GRUPO
async def group_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    group = query.data.split("_")[1]

    url = "https://api.football-data.org/v4/competitions/WC/standings"
    data = requests.get(url, headers=headers).json()

    standings = data.get("standings", [])

    msg = f"🏟️ Grupo {group}\n\n"

    found = False

    for g in standings:
        if group in g.get("group", ""):
            found = True

            for team in g["table"]:
                msg += f"{team['position']}. {team['team']['name']} - {team['points']} pts\n"

    if not found:
        msg += "No hay datos disponibles."

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver", callback_data="groups")]
    ]

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


# 📊 CLASIFICACIÓN GLOBAL
async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://api.football-data.org/v4/competitions/WC/standings"
    data = requests.get(url, headers=headers).json()

    standings = data.get("standings", [])

    msg = "📊 CLASIFICACIÓN MUNDIAL\n\n"

    for group in standings:
        msg += f"\n🏆 {group.get('group', 'GRUPO')}\n"

        for team in group["table"][:4]:
            msg += f"{team['position']}. {team['team']['name']} - {team['points']} pts\n"

    keyboard = [
        [InlineKeyboardButton("⬅️ Volver", callback_data="back")]
    ]

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


# 🔙 VOLVER AL MENÚ
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")],
        [InlineKeyboardButton("📊 Clasificación", callback_data="standings")]
    ]

    await query.edit_message_text(
        "🏆 MENÚ MUNDIAL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔀 ROUTER BOTONES
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = update.callback_query.data

    if data == "today":
        await today(update, context)

    elif data == "groups":
        await groups(update, context)

    elif data.startswith("group_"):
        await group_detail(update, context)

    elif data == "standings":
        await standings(update, context)

    elif data == "back":
        await back(update, context)


# 🤖 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("Bot con menú en marcha...")
app.run_polling()