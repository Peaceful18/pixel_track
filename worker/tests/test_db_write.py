from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from database.models import RawEvent
from worker.main import flush_to_db


@pytest.mark.asyncio
async def test_flush_to_db_saves_batch(db_session):
    events_batch = [
        RawEvent(
            raw_event_name="click_button",
            raw_event_type="ui_interaction",
            service="frontend_app",
            source="web",
            user_id="user_123",
            payload={"button_id": "submit_form"},
            timestamp=datetime.now(timezone.utc),
        ),
        RawEvent(
            raw_event_name="page_view",
            raw_event_type="navigation",
            service="frontend_app",
            source="mobile",
            user_id="user_456",
            payload={"path": "/dashboard"},
            timestamp=datetime.now(timezone.utc),
        ),
    ]
    await flush_to_db(events_batch, db_session)

    query = select(RawEvent).order_by(RawEvent.user_id)
    result = await db_session.execute(query)
    saved_events = result.scalars().all()

    assert len(saved_events) == 2

    event_1 = saved_events[0]
    assert event_1.user_id == "user_123"
    assert event_1.source == "web"
    assert event_1.raw_event_name == "click_button"
    assert event_1.payload == {"button_id": "submit_form"}

    event_2 = saved_events[1]
    assert event_2.user_id == "user_456"
    assert event_2.source == "mobile"
    assert event_2.raw_event_name == "page_view"
    assert event_2.payload == {"path": "/dashboard"}
