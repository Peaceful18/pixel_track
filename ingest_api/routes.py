from fastapi import APIRouter, Depends, HTTPException, status
from redis import RedisError
from redis import asyncio as aioredis

from .dependencies import get_redis_client
from .redis_client import check_health, push_event, push_event_batch
from .schemas import BatchEvent, Event, HealthResponse, TrackResponse

router = APIRouter()


@router.post(
    "/track", response_model=TrackResponse, status_code=status.HTTP_202_ACCEPTED
)
async def track_event(
    event: Event, redis: aioredis.Redis = Depends(get_redis_client)
) -> TrackResponse:
    try:
        event_json = event.model_dump_json()
        await push_event(event_json, redis)
        return TrackResponse(status="accepted", accepted=1, failed=0)
    except RedisError:
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis down)")


@router.post(
    "/track-batch", response_model=TrackResponse, status_code=status.HTTP_202_ACCEPTED
)
async def track_batch_event(
    batch_event: BatchEvent, redis: aioredis.Redis = Depends(get_redis_client)
) -> TrackResponse:
    try:
        batch_event_json = [e.model_dump_json() for e in batch_event.events]
        await push_event_batch(batch_event_json, redis)
        return TrackResponse(
            status="batch accepted", accepted=len(batch_event.events), failed=0
        )
    except RedisError:
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis down)")


@router.post("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(
    redis: aioredis.Redis = Depends(get_redis_client),
) -> HealthResponse:
    is_healthy = await check_health(redis)

    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis is down"
        )

    return HealthResponse(status="ok")
