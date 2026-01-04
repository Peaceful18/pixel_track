import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Project ---
    PROJECT_NAME: str = "Pixel Track"

    # --- Postgres ---
    # Дефолтні значення для локальної розробки (localhost)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("POSTGRES_DB", "pixel_track")

    # --- Redis ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_QUEUE_KEY: str = "events:raw"
    REDIS_PROCESSING_KEY: str = "events:processing"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
