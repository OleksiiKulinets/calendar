class InputDetectorService:

    async def detect(self, message):
        if getattr(message, "text", None):
            return {
                "type": "text",
                "message": message,
                "text": message.text,
                "meta": {}
            }

        if getattr(message, "voice", None):
            return {
                "type": "voice",
                "message": message,
                "text": None,
                "meta": {}
            }

        if getattr(message, "photo", None):
            return {
                "type": "image",
                "message": message,
                "text": None,
                "meta": {}
            }

        return {
            "type": "unknown",
            "message": message,
            "text": None,
            "meta": {}
        }