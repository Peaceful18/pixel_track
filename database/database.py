from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app_config.config import settings  # <--- Імпортуємо наш клас налаштувань

from .models import Base

# Більше ніяких os.getenv тут!
# Ми беремо готовий URL, який зібрав клас Settings
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, pool_size=10, max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Ініціалізація бази даних, створення таблиць."""
    print(
        f"Connecting to DB at: {settings.DB_HOST}:{settings.DB_PORT}"
    )  # Можна додати лог для налагодження
    print("Ініціалізація бази даних...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База даних ініціалізована.")


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


if __name__ == "__main__":
    import asyncio

    print("Ініціалізація бази даних...")
    asyncio.run(init_db())
    print("Готово.")
