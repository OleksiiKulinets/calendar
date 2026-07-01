from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select

from app.db.session import SessionLocal
from app.db.models import User, Calendar


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, action, confirmation_id = query.data.split(":")
    except ValueError:
        await query.edit_message_text("❌ Некоректні дані підтвердження")
        return

    confirmation_service = context.bot_data["confirmation"]

    draft = confirmation_service.get(confirmation_id)

    if not draft:
        await query.edit_message_text("❌ Подія застаріла або не знайдена")
        return

    if action == "cancel":
        confirmation_service.delete(confirmation_id)
        await query.edit_message_text("❌ Подію скасовано")
        return

    if action == "edit":
        await query.edit_message_text("✏️ Редагування поки не реалізовано")
        return

    if action == "create":
        await _create_event(
            draft,
            confirmation_service,
            query,
            context,
            confirmation_id
        )


async def _create_event(draft, confirmation_service, query, context, confirmation_id):
    payload = draft["payload"]
    user_id = draft["user_id"]

    with SessionLocal() as session:

        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if not user:
            await query.edit_message_text("❌ Користувача не знайдено")
            return

        calendar = session.execute(
            select(Calendar).where(
                Calendar.id == payload["calendar_id"]
            )
        ).scalar_one_or_none()

        if not calendar:
            await query.edit_message_text("❌ Календар не знайдено")
            return

        pipeline = context.bot_data["pipeline"]

        conflicts = await pipeline.calendar.check_conflicts(
            user.id,
            payload["start"],
            payload["end"]
        )

        if conflicts:
            await query.edit_message_text(
                "⚠️ Є конфлікти в розкладі. Подію не створено."
            )
            return

        event_data = {
            "title": payload["title"],
            "start": payload["start"],
            "end": payload["end"],
            "location_raw": payload.get("location"),
            "calendar_id": calendar.google_calendar_id
        }

        created = await pipeline.creator.create(
            session=session,
            user_id=user.id,
            event=event_data,
            calendar=calendar
        )

    confirmation_service.delete(confirmation_id)

    await query.edit_message_reply_markup(reply_markup=None)

    await query.message.reply_text(
        "✅ Подію успішно створено."
    )
