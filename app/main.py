import os
from datetime import datetime

from dotenv import load_dotenv

from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters)

from app.bot.handlers.start import start
from app.bot.handlers.calendar import select_calendar
from app.bot.handlers.confirmation import handle_confirmation
from app.bot.handlers.message import handle_message

from app.services.ai.openai_client import OpenAIClient

from app.services.event.event_extraction.prompts import PROMPT
from app.services.event.event_extraction.service import EventExtractionService
from app.services.event.event_pipeline.service import EventPipelineService
from app.services.event.event_validation.service import EventValidationService
from app.services.event.event_format.service import EventFormatService
from app.services.event.event_enrichment.link.service import EventLinkService
from app.services.event.event_enrichment.location.service import EventLocationService
from app.services.event.event_confirmation.service import EventConfirmationService
from app.services.event.event_creation.service import EventCreationService
from app.services.google_calendar.service import GoogleCalendarService
from app.services.input.detector.service import InputDetectorService
from app.services.input.image.service import ImageService
from app.services.input.voice.service import VoiceService

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

PROMPT = PROMPT.replace(
    "{{current_date}}",
    datetime.now().strftime("%Y-%m-%d")
)


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing")

    print("========== INIT ==========")

    ai_client = OpenAIClient()
    print("✓ OpenAI client")

    extractor = EventExtractionService(ai_client, PROMPT)
    print("✓ Event extractor")

    calendar_service = GoogleCalendarService()
    print("✓ Calendar service")

    voice_service = VoiceService(ai_client)
    image_service = ImageService(ai_client)
    detector = InputDetectorService()
    print("✓ Input detector")

    validator = EventValidationService()
    print("✓ Event validator")

    event_format = EventFormatService()
    print("✓ Event event_format")

    link = EventLinkService()
    location = EventLocationService()
    print("✓ Event location and link services")


    confirmation = EventConfirmationService()
    print("✓ Event confirmation service")

    creator = EventCreationService(calendar_service)
    print("✓ Event creation service")

    pipeline = EventPipelineService(extractor, calendar_service, detector, voice_service, image_service, validator, event_format, link, location, confirmation, creator)
    print("✓ Pipeline")

    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data["pipeline"] = pipeline
    app.bot_data["confirmation"] = confirmation

    print("BOT DATA:")
    print(app.bot_data)

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_calendar,
            pattern="^calendar:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            handle_confirmation,
            pattern="^confirmation:"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.VOICE | filters.PHOTO,
            handle_message
        ),
        group=0
    )

    print("========== BOT STARTED ==========")

    app.run_polling()


if __name__ == "__main__":
    main()