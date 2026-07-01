import uuid


class EventConfirmationService:

    def __init__(self):
        self._store = {}

    def create_draft(self, user_id: int, payload: dict) -> str:
        confirmation_id = str(uuid.uuid4())

        self._store[confirmation_id] = {
            "user_id": user_id,
            "payload": payload
        }

        return confirmation_id

    def get(self, confirmation_id: str):
        return self._store.get(confirmation_id)

    def delete(self, confirmation_id: str):
        self._store.pop(confirmation_id, None)