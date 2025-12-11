from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RawEvent(Base):
    __tablename__ = "raw_events"

    raw_event_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    raw_event_name: Mapped[str] = mapped_column(String(255), index=True)
    raw_event_type: Mapped[str] = mapped_column(String(100), index=True)
    service: Mapped[str] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<RawEvent(id={self.raw_event_id}, name={self.raw_event_name}, type={self.raw_event_type})>"
