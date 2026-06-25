from sqlalchemy import select

from app.db.models import User


class UserRepository:

    @staticmethod
    def get_by_telegram_id(
        session,
        telegram_user_id: int,
    ):
        return (
            session.execute(
                select(User).where(
                    User.telegram_user_id == telegram_user_id
                )
            )
            .scalar_one_or_none()
        )

    @staticmethod
    def create(
        session,
        *,
        telegram_user_id: int,
        telegram_chat_id: int,
        name: str,
    ):
        user = User(
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            name=name,
        )

        session.add(user)

        return user