import redis
from fastapi import APIRouter, HTTPException, status

from .redis_client import push_event, push_event_batch
from .schemas import BatchEvent, Event, TrackResponse

router = APIRouter()


@router.post(
    "/track", response_model=TrackResponse, status_code=status.HTTP_202_ACCEPTED
)
async def track_event(event: Event) -> TrackResponse:
    try:
        event_json = event.model_dump_json()
        push_event(event_json)
        return TrackResponse(status="accepted", accepted=1, failed=0)
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis down)")


@router.post(
    "/track-batch", response_model=TrackResponse, status_code=status.HTTP_202_ACCEPTED
)
async def track_batch_event(batch_event: BatchEvent) -> TrackResponse:
    try:
        batch_event_json = [e.model_dump_json() for e in batch_event.events]
        push_event_batch(batch_event_json)
        return TrackResponse(
            status="batch accepted", accepted=len(batch_event.events), failed=0
        )
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis down)")
