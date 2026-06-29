from pathlib import Path
import os


class VoiceService:

    def __init__(self, ai_client):
        self.ai = ai_client
        self.base_dir = Path("temp/voice")

    async def transcribe(self, message):
        print("\n[VOICE SERVICE] received voice data")

        self.base_dir.mkdir(parents=True, exist_ok=True)

        file_id = message.voice.file_unique_id
        file_path = self.base_dir / f"{file_id}.ogg"

        telegram_file = await message.voice.get_file()
        await telegram_file.download_to_drive(str(file_path))

        print(f"[VOICE SERVICE] saved to: {file_path}")

        try:
            text = await self.ai.transcribe_audio(str(file_path))
            print(f"[VOICE SERVICE] transcription: {text}")
            return text

        finally:
            if file_path.exists():
                file_path.unlink()
                print("[VOICE SERVICE] temp file removed")