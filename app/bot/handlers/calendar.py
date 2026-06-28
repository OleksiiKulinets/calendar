from sqlalchemy import select, update as sa_update
from app.db.models import User, Calendar
from app.db.session import SessionLocal


async def select_calendar(update_obj, context):
    query = update_obj.callback_query
    await query.answer()

    calendar_id = int(query.data.split(":")[1])

    with SessionLocal() as session:

        user_id = session.execute(
            select(User.id).where(
                User.telegram_user_id == query.from_user.id
            )
        ).scalar_one()

        calendar = session.execute(
            select(Calendar.id, Calendar.name).where(
                Calendar.id == calendar_id,
                Calendar.user_id == user_id
            )
        ).first()

        if not calendar:
            await query.edit_message_text("❌ Календар не знайдено")
            return

        cal_id, cal_name = calendar

        session.execute(
            sa_update(User)
            .where(User.id == user_id)
            .values(selected_calendar_id=cal_id)
        )

        session.commit()

    await query.edit_message_text(
        f"✅ Обрано календар:\n{cal_name}"
    )