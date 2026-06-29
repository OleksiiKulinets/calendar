from sqlalchemy import select
from app.db.models import User, Calendar
from datetime import datetime, timedelta
from app.db.session import SessionLocal


class EventPipelineService:

    def __init__(self, extractor, calendar_service, detector, voice_service, image_service, creator):
        self.extractor = extractor
        self.calendar = calendar_service
        self.detector = detector
        self.voice_service = voice_service
        self.image_service = image_service
        self.creator = creator

    async def process(self, message: str, telegram_user_id: int):

        print("\n================ PIPELINE START ================")

        # =========================================================
        # 1. USER MESSAGE
        # =========================================================
        print("\n[STEP 1] USER MESSAGE RECEIVED")
        print(message)

        # =========================================================
        # 2. DETECT INPUT TYPE
        # =========================================================
        print("\n[STEP 2] INPUT TYPE DETECTION")

        input_data = await self.detector.detect(message)

        print(f"[TYPE] {input_data['type']}")

        # =========================================================
        # 3. TRANSCRIPTION / IMAGE ANALYSIS
        # =========================================================
        print("\n[STEP 3] MEDIA PROCESSING → TEXT NORMALIZATION")

        if input_data["type"] == "voice":
            text = await self.voice_service.transcribe(input_data["message"])

        elif input_data["type"] == "image":
            text = await self.image_service.extract_text(input_data["message"])

        else:
            text = input_data["text"]

        if not text:
            print("❌ Empty text after normalization")
            return {"error": "empty_input"}

        print(f"[NORMALIZED TEXT] {text}")

        # =========================================================
        # 4. STRUCTURED EXTRACTION
        # =========================================================
        print("\n[STEP 4] STRUCTURED EVENT EXTRACTION")

        event = await self.extractor.extract(text)

        print("[EXTRACTED EVENT]")
        print(event)

        # =========================================================
        # 5. VALIDATION (DATE / TIME / DURATION)
        # =========================================================
        print("\n[STEP 5] VALIDATION OF DATE / TIME / DURATION")

        start = self._parse_datetime(event["date"], event["start_time"])

        if not start:
            print("❌ Missing date/time → cannot continue pipeline")
            return {
                "error": "missing_datetime",
                "raw": event
            }

        duration = event.get("duration_minutes") or 60
        end = start + timedelta(minutes=duration)

        print(f"START: {start}")
        print(f"END: {end}")

        # =========================================================
        # 6. FORMAT DETECTION
        # =========================================================
        print("\n[STEP 6] EVENT FORMAT DETECTION")
        print(event.get("event_format"))

        # =========================================================
        # 7. LOCATION / LINK PROCESSING
        # =========================================================
        print("\n[STEP 7] LOCATION / ONLINE LINK HANDLING")
        print(event.get("location_raw"))

        # =========================================================
        # 8. MISSING DATA CLARIFICATION (FUTURE STEP)
        # =========================================================
        print("\n[STEP 8] MISSING DATA CHECK (NOT IMPLEMENTED)")
        # TODO: ask user follow-up questions if needed

        # =========================================================
        # DB CONTEXT START
        # =========================================================
        with SessionLocal() as session:

            user = session.execute(
                select(User).where(
                    User.telegram_user_id == telegram_user_id
                )
            ).scalar_one_or_none()

            if not user:
                raise ValueError(
                    f"User not found in DB: {telegram_user_id}"
                )

            # =========================================================
            # 9. CONFLICT CHECK
            # =========================================================
            print("\n[STEP 9] CONFLICT CHECK")

            conflicts = await self.calendar.check_conflicts(
                user.id,
                start,
                end
            )

            print(f"CONFLICTS: {conflicts}")

            # =========================================================
            # 10. PREVIEW BUILD
            # =========================================================
            print("\n[STEP 10] PREVIEW BUILD")

            preview = {
                "title": event["title"],
                "start": start,
                "end": end,
                "location": event.get("location_raw"),
                "format": event.get("event_format"),
                "conflict": len(conflicts) > 0
            }

            print(preview)

            # =========================================================
            # 11. USER CONFIRMATION (MISSING IN LOGIC)
            # =========================================================
            print("\n[STEP 11] USER CONFIRMATION (NOT IMPLEMENTED)")
            # TODO: send preview to Telegram + wait callback

            # =========================================================
            # 12. RECHECK CONFLICTS (AFTER CONFIRMATION)
            # =========================================================
            print("\n[STEP 12] RECHECK CONFLICTS (NOT IMPLEMENTED)")

            calendar = session.execute(
                select(Calendar).where(
                    Calendar.id == user.selected_calendar_id
                )
            ).scalar_one_or_none()

            if not calendar:
                raise ValueError("Selected calendar not found")

            # =========================================================
            # 13. CREATE EVENT
            # =========================================================
            print("\n[STEP 13] CREATE EVENT")

            created = await self.creator.create(
                session=session,
                user_id=user.id,
                event={
                    "title": event["title"],
                    "start": start,
                    "end": end,
                    "location_raw": event.get("location_raw"),
                    "calendar_id": calendar.google_calendar_id
                },
                calendar=calendar
            )

        print("\n[PIPELINE RESULT]")
        print(created)

        print("\n================ PIPELINE END ================")

        return {
            "raw": event,
            "preview": preview
        }

    def _parse_datetime(self, date_str, time_str):
        if not date_str or not time_str:
            return None

        return datetime.fromisoformat(f"{date_str}T{time_str}:00")