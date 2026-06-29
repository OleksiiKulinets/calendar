import os

from openai import AsyncOpenAI


class OpenAIClient:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def extract_event(self, prompt: str, message: str):
        response = await self.client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    async def transcribe_audio(self, file_path: str):

        print("[OPENAI] Sending audio to Whisper...")

        with open(file_path, "rb") as audio:

            transcript = await self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
            )

        print("[OPENAI] Transcription complete")

        return transcript.text

    async def analyze_image(self, file_path: str):

        print("[OPENAI] Sending image to Vision...")

        with open(file_path, "rb") as image:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract all useful text from this image. "
                            "If this is an event, include title, date, time, location. "
                            "Return clean raw text only."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Read this image and extract all event-related text."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{self._encode_image(image)}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.2
            )

        print("[OPENAI] Image analysis complete")

        return response.choices[0].message.content

    def _encode_image(self, image_file):
        import base64
        return base64.b64encode(image_file.read()).decode("utf-8")