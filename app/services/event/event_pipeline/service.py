from sqlalchemy import select
from app.db.models import User, Calendar
from datetime import datetime, timedelta
from app.db.session import SessionLocal

class EventPipelineService:

    def __init__(self, extractor, calendar_service):
        self.extractor = extractor
        self.calendar = calendar_service

    async def process(self, message: str, user_id: int):

        print("\n[PIPELINE] STEP 1 - EXTRACT")

        event = await self.extractor.extract(message)

        print("[PIPELINE] RAW EVENT:")
        print(event)

        print("[PIPELINE] STEP 2 - PARSE DATETIME")

        start = self._parse_datetime(event["date"], event["start_time"])

        print(f"[PIPELINE] START: {start}")

        duration = event.get("duration_minutes") or 60
        end = start + timedelta(minutes=duration)

        print(f"[PIPELINE] END: {end}")

        print("[PIPELINE] STEP 3 - CONFLICT CHECK")

        conflicts = await self.calendar.check_conflicts(
            user_id,
            start,
            end
        )

        print(f"[PIPELINE] CONFLICTS: {conflicts}")

        print("[PIPELINE] STEP 4 - BUILD PREVIEW")

        preview = {
            "title": event["title"],
            "start": start,
            "end": end,
            "location": event.get("location_raw"),
            "format": event.get("event_format"),
            "conflict": len(conflicts) > 0
        }

        print("[PIPELINE] STEP 5 - CREATE EVENT")

        with SessionLocal() as session:

            user = session.execute(
                select(User).where(User.telegram_user_id == user_id)
            ).scalar_one_or_none()

            if not user:
                raise ValueError(f"User not found in DB: {user_id}")

            calendar = session.execute(
                select(Calendar).where(Calendar.id == user.selected_calendar_id)
            ).scalar_one_or_none()

            if not calendar:
                raise ValueError("Selected calendar not found")

            created = await self.calendar.create_event(
                session,
                user.telegram_user_id,
                {
                    "title": event["title"],
                    "start": start,
                    "end": end,
                    "location": event.get("location_raw"),
                    "calendar_id": calendar.google_calendar_id
                }
            )

        print("[PIPELINE] CREATED EVENT:")
        print(created)

        print("[PIPELINE] DONE")

        return {
            "raw": event,
            "preview": preview
        }

    def _parse_datetime(self, date_str, time_str):
        return datetime.fromisoformat(
            f"{date_str}T{time_str}:00"
        )