from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/ingest")
