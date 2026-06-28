from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EventDraft(BaseModel):
    title: str
    start: datetime
    end: datetime
    is_online: bool = False
    location: Optional[str] = None
    reminder_minutes: int = 30