import json
from app.services.ai.openai_client import OpenAIClient


class EventExtractionService:

    def __init__(self, ai_client: OpenAIClient, prompt: str):
        self.ai = ai_client
        self.prompt = prompt

    async def extract(self, message: str):
        raw = await self.ai.extract_event(self.prompt, message)

        data = json.loads(raw)

        return data
        
    async def extract(self, message: str):
        raw = await self.ai.extract_event(self.prompt, message)

        print("RAW GPT RESPONSE:")
        print(raw)

        data = json.loads(raw)

        return data