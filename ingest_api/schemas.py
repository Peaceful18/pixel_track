from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Event(BaseModel):
    event: str
    type: Literal["sql", "http", "business", "system"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict | None = None
    user_id: int | None = None
    source: str
    service: str | None = None


class BatchEvent(BaseModel):
    events: list[Event]


class TrackResponse(BaseModel):
    status: str
    accepted: int
    failed: int
    errors: list[str] | None = None
