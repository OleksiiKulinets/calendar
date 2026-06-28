from sqlalchemy import select

from app.db.models import GoogleAccount


class GoogleAccountRepository:

    @staticmethod
    def get_by_user_id(
        session,
        user_id: int,
    ):
        return (
            session.execute(
                select(GoogleAccount).where(
                    GoogleAccount.user_id == user_id
                )
            )
            .scalar_one_or_none()
        )

    @staticmethod
    def create(
        session,
        *,
        user_id: int,
        google_email: str,
        access_token: str,
        refresh_token: str | None,
        expires_at,
    ):
        account = GoogleAccount(
            user_id=user_id,
            google_email=google_email,
            access_token_encrypted=access_token,
            refresh_token_encrypted=refresh_token,
            token_expires_at=expires_at,
        )

        session.add(account)

        return account