from openai import AsyncOpenAI
import os


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