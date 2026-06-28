import httpx

from app.repositories.google_account import GoogleAccountRepository
from app.services.crypto.service import CryptoService


GOOGLE_CALENDAR_LIST_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


class GoogleCalendarService:

    @staticmethod
    async def get_access_token(session, user_id: int) -> str:
        account = GoogleAccountRepository.get_by_user_id(session, user_id)

        if not account:
            raise ValueError("Google account not found")

        return CryptoService.decrypt(account.access_token_encrypted)

    @staticmethod
    async def fetch_calendars(session, user_id: int):
        """
        ЄДИНА функція для Google API
        """
        token = await GoogleCalendarService.get_access_token(session, user_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_CALENDAR_LIST_URL,
                headers={"Authorization": f"Bearer {token}"}
            )

        data = response.json()
        return data.get("items", [])