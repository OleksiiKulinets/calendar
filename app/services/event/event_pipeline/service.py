from sqlalchemy import select
from app.db.models import User, Calendar
from datetime import datetime, timedelta
from app.db.session import SessionLocal


class EventPipelineService:

    def __init__(self, extractor, calendar_service, detector, voice_service, image_service, validator, event_format, link, location, confirmation, creator):
        self.extractor = extractor
        self.calendar = calendar_service
        self.detector = detector
        self.voice_service = voice_service
        self.image_service = image_service
        self.validator = validator
        self.event_format = event_format
        self.link = link
        self.location = location
        self.confirmation = confirmation
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

        validated = self.validator.validate(event)

        if not validated["success"]:
            print(f"❌ Validation failed: {validated['error']}")

            return {
                "error": validated["error"],
                "raw": event
            }

        start = validated["start"]
        end = validated["end"]

        print(f"START: {start}")
        print(f"END: {end}")

        # =========================================================
        # 6. FORMAT DETECTION
        # =========================================================
        print("\n[STEP 6] FORMAT DETECTION")

        event["event_format"] = self.event_format.detect(event)

        print(event["event_format"])

        # =========================================================
        # 7. LOCATION / LINK PROCESSING !!!
        # =========================================================
        print("\n[STEP 7] LOCATION / ONLINE LINK HANDLING")
        print(event.get("location_raw"))
        print(event.get("conference_urls"))

        # =========================================================
        # 8. MISSING DATA CLARIFICATION !!!
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
            # 9. CONFLICT CHECK !!!
            # =========================================================
            print("\n[STEP 9] CONFLICT CHECK")

            conflicts = await self.calendar.check_conflicts(
                user.id,
                start,
                end
            )

            print(f"CONFLICTS: {conflicts}")

            # =========================================================
            # 10. PREVIEW BUILD  !!
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
            # 11. USER CONFIRMATION (MISSING IN LOGIC) !!! DB updates
            # =========================================================
            print("\n[STEP 11] USER CONFIRMATION")

            confirmation_payload = {
                "title": event["title"],
                "start": start,
                "end": end,
                "location": event.get("location_raw"),
                "event_format": event.get("event_format"),
                "user_id": user.id,
                "calendar_id": user.selected_calendar_id,
                "conflicts": len(conflicts) > 0
            }

            confirmation_id = self.confirmation.create_draft(
                user_id=user.id,
                payload=confirmation_payload
            )

            preview["confirmation_id"] = confirmation_id

            # =========================================================
            # 12. RECHECK CONFLICTS (AFTER CONFIRMATION) !!!
            # =========================================================
            print("\n[STEP 12] RECHECK CONFLICTS (WAITING CONFIRMATION)")

            draft = self.confirmation.get(confirmation_id)

            if not draft:
                return {"error": "draft_not_found"}

            conflicts = await self.calendar.check_conflicts(
                user.id,
                start,
                end
            )

            print(f"CONFLICTS: {conflicts}")

        print("\n[PIPELINE RESULT]")

        print("\n================ PIPELINE END ================")

        return {
            "raw": event,
            "preview": preview,
            "status": "pending_confirmation"
        }