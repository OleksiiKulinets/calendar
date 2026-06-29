class EventCreationService:

    def __init__(self, calendar_service):
        self.calendar_service = calendar_service

    async def create(self, session, user_id, event, calendar):
        return await self.calendar_service.create_event(
            session,
            user_id,
            {
                "title": event["title"],
                "start": event["start"],
                "end": event["end"],
                "location": event.get("location_raw"),
                "calendar_id": calendar.google_calendar_id
            }
        )