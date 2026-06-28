from datetime import datetime, timedelta, UTC

from app.services.crypto.service import CryptoService
from app.repositories.google_account import GoogleAccountRepository
from app.repositories.user import UserRepository


class GoogleAccountService:

    @staticmethod
    def create_or_update(
        session,
        *,
        telegram_user_id: int,
        google_email: str,
        access_token: str,
        refresh_token: str | None,
        expires_in: int,
    ):

        user = UserRepository.get_by_telegram_id(
            session,
            telegram_user_id,
        )

        if not user:
            raise ValueError("User not found")

        expires_at = datetime.now(UTC) + timedelta(
            seconds=expires_in
        )

        account = GoogleAccountRepository.get_by_user_id(
            session,
            user.id,
        )

        if account:

            account.google_email = google_email

            account.access_token_encrypted = CryptoService.encrypt(
                access_token
            )

            if refresh_token:
                account.refresh_token_encrypted = CryptoService.encrypt(
                    refresh_token
                )
                

            account.token_expires_at = expires_at

            return account

        return GoogleAccountRepository.create(
            session,
            user_id=user.id,
            google_email=google_email,
            access_token=CryptoService.encrypt(access_token),
            refresh_token=(
                CryptoService.encrypt(refresh_token)
                if refresh_token
                else None
            ),
            expires_at=expires_at,
        )