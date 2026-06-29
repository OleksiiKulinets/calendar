import os
from datetime import datetime

from dotenv import load_dotenv

from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters)

from app.bot.handlers.start import start
from app.bot.handlers.calendar import select_calendar
from app.bot.handlers.message import handle_message

from app.services.ai.openai_client import OpenAIClient

from app.services.event.event_extraction.prompts import PROMPT
from app.services.event.event_extraction.service import EventExtractionService
from app.services.event.event_pipeline.service import EventPipelineService
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

    creator = EventCreationService(calendar_service)
    pipeline = EventPipelineService(extractor, calendar_service, detector, voice_service, image_service, creator)
    print("✓ Pipeline")

    app = Application.builder().token(BOT_TOKEN).build()

    app.bot_data["pipeline"] = pipeline

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