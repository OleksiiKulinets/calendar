from pathlib import Path


class ImageService:

    def __init__(self, ai_client):
        self.ai = ai_client
        self.base_dir = Path("temp/image")

    async def extract_text(self, message):
        print("\n[IMAGE SERVICE] received image data")

        self.base_dir.mkdir(parents=True, exist_ok=True)

        photo = message.photo[-1]
        file_id = photo.file_unique_id

        file_path = self.base_dir / f"{file_id}.jpg"

        file = await photo.get_file()
        await file.download_to_drive(str(file_path))

        print(f"[IMAGE SERVICE] saved to: {file_path}")

        text = await self.ai.analyze_image(str(file_path))

        print("[IMAGE SERVICE] extracted text:", text)

        return text