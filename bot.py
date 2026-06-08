import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import os

TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

headers = {"X-Auth-Token": API_KEY}

# 📊 START MENU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 MENU NUEVO FUNCIONANDO",
        reply_markup=reply_markup
    )

# 📅 PARTIDOS
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = "https://api.football-data.org/v4/matches"
    data = requests.get(url, headers=headers).json()

    matches = data.get("matches", [])

    msg = "📅 PARTIDOS HOY:\n\n"

    for m in matches[:10]:
        msg += f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} - {m['status']}\n"

    await query.edit_message_text(msg)

# 🌍 GRUPOS MENU
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Grupo A", callback_data="group_A"),
         InlineKeyboardButton("Grupo B", callback_data="group_B")],
        [InlineKeyboardButton("Grupo C", callback_data="group_C"),
         InlineKeyboardButton("Grupo D", callback_data="group_D")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="back")]
    ]

    await query.edit_message_text(
        "🌍 Selecciona un grupo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📊 DETALLE DE GRUPOS
async def group_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    group = query.data.split("_")[1]

    url = "https://api.football-data.org/v4/competitions/WC/standings"
    data = requests.get(url, headers=headers).json()

    standings = data.get("standings", [])

    msg = f"🏟️ Grupo {group}\n\n"

    for g in standings:
        if group in g.get("group", ""):
            for team in g["table"]:
                msg += f"{team['position']}. {team['team']['name']} - {team['points']} pts\n"

    keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="groups")]]

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# 🔙 VOLVER
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("🌍 Grupos", callback_data="groups")]
    ]

    await query.edit_message_text(
        "🏆 MENÚ MUNDIAL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔀 ROUTER DE BOTONES
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    if data == "today":
        await today(update, context)

    elif data == "groups":
        await groups(update, context)

    elif data.startswith("group_"):
        await group_detail(update, context)

    elif data == "back":
        await back(update, context)


# 🤖 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("Bot con menú en marcha...")
app.run_polling()