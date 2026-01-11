import pytest
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app_config.config import settings
from database.models import Base


# --- 1. Redis ---
@pytest.fixture
async def redis_client():
    redis = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    yield redis
    await redis.flushdb()
    await redis.aclose()


# --- 2. Async Engine ---
@pytest.fixture(scope="session")
async def db_engine():
    # Створюємо Engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Створюємо таблиці (це замінює init_db)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Видаляємо таблиці в кінці
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# --- 3. Helper для очищення (ВИПРАВЛЕНО text()) ---
async def truncate_tables(session):
    tables = Base.metadata.sorted_tables
    if not tables:
        return

    table_names = [f'"{table.name}"' for table in tables]

    sql_string = f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;"
    sql_command = text(sql_string)

    await session.execute(sql_command)
    await session.commit()


# --- 4. Session Fixture ---
@pytest.fixture
async def db_session(db_engine):
    AsyncSessionLocal = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session
        # Чистимо базу після кожного тесту
        await truncate_tables(session)


# --- 5. Init DB Hook ---
@pytest.fixture(scope="session", autouse=True)
async def init_db(db_engine):
    """
    Тригер, щоб db_engine запустився і створив таблиці.
    """
    yield
