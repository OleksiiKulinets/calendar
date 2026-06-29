from datetime import datetime, timedelta, UTC
import httpx

from app.services.crypto.service import CryptoService
from app.repositories.google_account import GoogleAccountRepository


class GoogleAccountService:

    @staticmethod
    def create_or_update(
        session,
        *,
        user_id: int,
        google_email: str,
        access_token: str,
        refresh_token: str | None,
        expires_in: int,
    ):
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        account = GoogleAccountRepository.get_by_user_id(session, user_id)

        encrypted_access = CryptoService.encrypt(access_token)
        encrypted_refresh = CryptoService.encrypt(refresh_token) if refresh_token else None

        if account:
            account.google_email = google_email
            account.access_token_encrypted = encrypted_access

            if refresh_token:
                account.refresh_token_encrypted = encrypted_refresh

            account.token_expires_at = expires_at
            return account

        return GoogleAccountRepository.create(
            session,
            user_id=user_id,
            google_email=google_email,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            expires_at=expires_at,
        )

    @staticmethod
    def get_by_user_id(session, user_id: int):
        return GoogleAccountRepository.get_by_user_id(session, user_id)

    @staticmethod
    def is_token_expired(account) -> bool:
        if not account or not account.token_expires_at:
            return True
        return account.token_expires_at <= datetime.now(UTC)

    @staticmethod
    def _decrypt(account):
        return {
            "access_token": CryptoService.decrypt(account.access_token_encrypted),
            "refresh_token": (
                CryptoService.decrypt(account.refresh_token_encrypted)
                if account.refresh_token_encrypted
                else None
            ),
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": "YOUR_GOOGLE_CLIENT_ID",
                    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

        data = response.json()

        if "access_token" not in data:
            raise Exception(f"Failed to refresh token: {data}")

        return {
            "access_token": data["access_token"],
            "expires_in": data["expires_in"],
        }

    @staticmethod
    async def get_valid_access_token(session, user_id: int) -> str:
        account = GoogleAccountRepository.get_by_user_id(session, user_id)

        if not account:
            raise Exception("Google account not connected")

        tokens = GoogleAccountService._decrypt(account)

        if not GoogleAccountService.is_token_expired(account):
            return tokens["access_token"]

        if not tokens["refresh_token"]:
            raise Exception("No refresh token available")

        refreshed = await GoogleAccountService.refresh_access_token(
            tokens["refresh_token"]
        )

        new_access_token = refreshed["access_token"]
        expires_at = datetime.now(UTC) + timedelta(
            seconds=refreshed["expires_in"]
        )

        account.access_token_encrypted = CryptoService.encrypt(new_access_token)
        account.token_expires_at = expires_at

        return new_access_token