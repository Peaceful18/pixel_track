from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Event(BaseModel):
    event: str
    type: Literal["sql", "http", "business", "system"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict | None = None
    user_id: str | None = None
    source: str
    service: str

    @field_validator("payload")
    def validate_payload(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("payload cannot be empty dict")
        return v


class BatchEvent(BaseModel):
    events: list[Event]


class TrackResponse(BaseModel):
    status: str
    accepted: int
    failed: int
    errors: list[str] | None = None
