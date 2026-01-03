from contextlib import asynccontextmanager

from fastapi import FastAPI

from infra.redis_provider import redis_provider

from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    redis_provider.init_pool()
    yield
    await redis_provider.close_pool()
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/ingest")
