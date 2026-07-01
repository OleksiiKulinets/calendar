from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("HANDLE MESSAGE")
    print(id(context.application))
    print(context.bot_data)

    user_id = update.effective_user.id

    result = await context.bot_data["pipeline"].process(
        update.message,
        user_id
    )

    if "error" in result:
        await update.message.reply_text(
            "❌ Не вдалося створити подію. Перевір формат повідомлення."
        )
        return

    p = result.get("preview", {})

    title = p.get("title", "Без назви")
    start = p.get("start")
    end = p.get("end")
    location = p.get("location", "—")
    event_format = p.get("format", "—")
    confirmation_id = p.get("confirmation_id")

    date = start.date().isoformat() if hasattr(start, "date") else "—"
    time_range = f"{start.time()} – {end.time()}" if start and end else "—"

    text = (
        f"📌 <b>{title}</b>\n\n"
        f"📅 {date}\n"
        f"🕒 {time_range}\n"
    )

    if location:
        text += f"📍 {location}\n"

    text += (
        "\n"
        "⚙️ <b>Деталі</b>\n"
        f"• Формат: {event_format}\n"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Створити",
                callback_data=f"confirmation:create:{confirmation_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ Змінити",
                callback_data=f"confirmation:edit:{confirmation_id}"
            ),
            InlineKeyboardButton(
                "❌ Скасувати",
                callback_data=f"confirmation:cancel:{confirmation_id}"
            )
        ]
    ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )