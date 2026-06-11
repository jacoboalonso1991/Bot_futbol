import os
import requests

from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ==================================
# CONFIG
# ==================================

TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY")

HEADERS = {
    "X-Auth-Token": API_KEY
}

BASE_URL = "https://api.football-data.org/v4"


# ==================================
# HELPERS
# ==================================

def api_get(endpoint):
    try:
        r = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=HEADERS,
            timeout=15
        )

        if r.status_code != 200:
            return None

        return r.json()

    except Exception:
        return None


# ==================================
# START
# ==================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🏆 Grupos", callback_data="groups")],
        [InlineKeyboardButton("📊 Clasificación", callback_data="standings")],
        [InlineKeyboardButton("📅 Partidos hoy", callback_data="today")],
        [InlineKeyboardButton("📆 Próximos partidos", callback_data="next")],
        [InlineKeyboardButton("⚽ Últimos resultados", callback_data="results")]
    ]

    await update.message.reply_text(
        "🏆 BOT MUNDIAL 2026\n\nSelecciona una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================================
# GRUPOS
# ==================================

async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = api_get("/competitions/WC/standings")

    if not data:
        await query.edit_message_text(
            "❌ No se pudieron cargar los grupos."
        )
        return

    msg = "🏆 GRUPOS DEL MUNDIAL\n\n"

    standings = data.get("standings", [])

    for group in standings:

        group_name = group.get("group", "")

        if not group_name:
            continue

        msg += f"{group_name}\n"

        for team in group["table"]:
            msg += f"• {team['team']['name']}\n"

        msg += "\n"

    await query.edit_message_text(msg[:4000])


# ==================================
# CLASIFICACIÓN
# ==================================

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = api_get("/competitions/WC/standings")

    if not data:
        await query.edit_message_text(
            "❌ No se pudo cargar la clasificación."
        )
        return

    msg = "📊 CLASIFICACIÓN\n\n"

    standings = data.get("standings", [])

    for group in standings:

        group_name = group.get("group", "")

        if not group_name:
            continue

        msg += f"🏆 {group_name}\n"

        for team in group["table"]:

            msg += (
                f"{team['position']}. "
                f"{team['team']['name']} "
                f"({team['points']} pts)\n"
            )

        msg += "\n"

    await query.edit_message_text(msg[:4000])


# ==================================
# PARTIDOS HOY
# ==================================

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = api_get("/competitions/WC/matches")

    if not data:
        await query.edit_message_text(
            "❌ No se pudieron cargar los partidos."
        )
        return

    today_date = datetime.utcnow().date()

    matches_today = []

    for match in data.get("matches", []):

        utc_date = match["utcDate"][:10]

        if utc_date == str(today_date):
            matches_today.append(match)

    if not matches_today:

        await query.edit_message_text(
            "📅 No hay partidos del Mundial hoy."
        )
        return

    msg = "📅 PARTIDOS DE HOY\n\n"

    for match in matches_today:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        kickoff = match["utcDate"][11:16]

        msg += f"🕒 {kickoff} UTC\n{home} vs {away}\n\n"

    await query.edit_message_text(msg[:4000])


# ==================================
# PRÓXIMOS PARTIDOS
# ==================================

async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = api_get("/competitions/WC/matches")

    if not data:
        await query.edit_message_text(
            "❌ No se pudieron cargar los partidos."
        )
        return

    msg = "📆 PRÓXIMOS PARTIDOS\n\n"

    count = 0

    for match in data.get("matches", []):

        if count >= 10:
            break

        if match.get("status") == "SCHEDULED":

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            date = match["utcDate"][:10]
            hour = match["utcDate"][11:16]

            msg += (
                f"📅 {date} {hour}\n"
                f"{home} vs {away}\n\n"
            )

            count += 1

    await query.edit_message_text(msg[:4000])


# ==================================
# ÚLTIMOS RESULTADOS
# ==================================

async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = api_get("/competitions/WC/matches")

    if not data:
        await query.edit_message_text(
            "❌ No se pudieron cargar los resultados."
        )
        return

    finished = []

    for match in data.get("matches", []):

        if match.get("status") == "FINISHED":
            finished.append(match)

    if not finished:
        await query.edit_message_text(
            "⚽ Todavía no hay resultados disponibles."
        )
        return

    finished = finished[-10:]

    msg = "⚽ ÚLTIMOS RESULTADOS\n\n"

    for match in reversed(finished):

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        home_score = match["score"]["fullTime"]["home"]
        away_score = match["score"]["fullTime"]["away"]

        msg += f"{home} {home_score}-{away_score} {away}\n"

    await query.edit_message_text(msg[:4000])


# ==================================
# BOTONES
# ==================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = update.callback_query.data

    if data == "groups":
        await groups(update, context)

    elif data == "standings":
        await standings(update, context)

    elif data == "today":
        await today(update, context)

    elif data == "next":
        await next_matches(update, context)

    elif data == "results":
        await results(update, context)


# ==================================
# MAIN
# ==================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("🏆 BOT MUNDIAL 2026 ONLINE")

app.run_polling()