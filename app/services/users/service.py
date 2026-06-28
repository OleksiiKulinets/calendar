from app.repositories.user import UserRepository


class UserService:

    @staticmethod
    def create_or_update_user(
        session,
        *,
        telegram_user_id: int,
        telegram_chat_id: int,
        name: str,
        timezone: str,
        default_city: str,
        default_country: str,
    ):

        user = UserRepository.get_by_telegram_id(
            session,
            telegram_user_id,
        )

        if user:
            user.telegram_chat_id = telegram_chat_id
            user.name = name

            return user

        return UserRepository.create(
            session,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            name=name,
            timezone=timezone,
            default_city=default_city,
            default_country=default_country,
        )