from sqlalchemy import select
from app.db.models import User


class UserResolver:

    @staticmethod
    def get_user(session, telegram_user_id: int) -> User:
        user = session.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        ).scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        return user
    @staticmethod
    def get_user_by_telegram(session, telegram_user_id: int) -> User:
        return session.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        ).scalar_one()