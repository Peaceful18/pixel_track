from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Event(BaseModel):
    event: str
    type: Literal["sql", "http", "business", "system"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] | None = None
    user_id: str | None = None
    source: str
    service: str

    @field_validator("payload")
    def validate_payload(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("payload cannot be empty dict")
        return v

    @model_validator(mode="after")
    def check_payload_contract(self):
        """
        Перевіряємо контракт:
        Якщо це технічний лог (sql/http), то в payload МАЄ бути 'raw_log'.
        """
        event_type = self.type
        payload = self.payload or {}
        parsable_types = ["sql", "http"]
        if event_type in parsable_types:
            if "raw_log" not in payload:
                raise ValueError(
                    f"Payload for {event_type} event must contain 'raw_log' key"
                )
            if not isinstance(payload["raw_log"], str):
                raise ValueError(
                    f"Payload for {event_type} event 'raw_log' must be a string"
                )
        return self


class BatchEvent(BaseModel):
    events: list[Event]


class TrackResponse(BaseModel):
    status: str
    accepted: int
    failed: int
    errors: list[str] | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
