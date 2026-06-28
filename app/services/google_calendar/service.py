import httpx

from app.services.users.resolver import UserResolver
from app.repositories.google_account import GoogleAccountRepository
from app.services.crypto.service import CryptoService

GOOGLE_CALENDAR_LIST_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


class GoogleCalendarService:

    @staticmethod
    async def get_user(session, telegram_user_id: int):
        return UserResolver.get_user(session, telegram_user_id)
    @staticmethod
    async def get_access_token(session, telegram_user_id: int):

        user = UserResolver.get_user(session, telegram_user_id)

        account = GoogleAccountRepository.get_by_user_id(session, user.id)

        if not account:
            raise ValueError("Google account not found")

        return CryptoService.decrypt(account.access_token_encrypted)

    @staticmethod
    async def fetch_calendars(session, telegram_user_id: int):

        token = await GoogleCalendarService.get_access_token(session, telegram_user_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_CALENDAR_LIST_URL,
                headers={"Authorization": f"Bearer {token}"}
            )

        return response.json().get("items", [])

    async def create_event(self, session, telegram_user_id: int, event: dict):

        token = await self.get_access_token(session, telegram_user_id)

        calendar_id = event.get("calendar_id")

        url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

        body = {
            "summary": event["title"],
            "start": {
                "dateTime": event["start"].isoformat(),
                "timeZone": "Europe/Kyiv"
            },
            "end": {
                "dateTime": event["end"].isoformat(),
                "timeZone": "Europe/Kyiv"
            },
            "location": event.get("location")
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=body,
                headers={"Authorization": f"Bearer {token}"}
            )

        return response.json()

    async def check_conflicts(self, user_id: int, start, end):
        return []