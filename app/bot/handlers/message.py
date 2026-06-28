from telegram import Update
from telegram.ext import ContextTypes

from app.services.event.event_pipeline.service import EventPipelineService


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("HANDLE MESSAGE")
    print(id(context.application))
    print(context.bot_data)
    text = update.message.text
    user_id = update.effective_user.id

    result = await context.bot_data["pipeline"].process(
        text,
        user_id
    )

    p = result["preview"]

    await update.message.reply_text(
        f"""
📌 {p['title']}

🕒 {p['start']} → {p['end']}
📍 {p['location'] or "—"}

⚠️ Конфлікт: {"є" if p['conflict'] else "нема"}
        """
    )