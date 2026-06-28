from sqlalchemy import select
from app.db.models import Calendar


class GoogleCalendarRepository:

    @staticmethod
    def get_by_id(session, calendar_id: int):
        return session.get(Calendar, calendar_id)

    @staticmethod
    def get_by_user(session, user_id: int):
        return session.execute(
            select(Calendar).where(Calendar.user_id == user_id)
        ).scalars().all()

    @staticmethod
    def get_by_user_and_google_id(session, user_id: int, google_calendar_id: str):
        return session.execute(
            select(Calendar).where(
                Calendar.user_id == user_id,
                Calendar.google_calendar_id == google_calendar_id
            )
        ).scalar_one_or_none()