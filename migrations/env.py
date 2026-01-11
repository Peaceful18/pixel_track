import asyncio
import os
import sys
from logging.config import fileConfig

# Додаємо корінь проекту в шлях пошуку модулів
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.getcwd())

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app_config.config import settings

# Імпортуємо Base та всі моделі. Оскільки вони в одному файлі,
# цей імпорт автоматично зареєструє їх у метаданих.
from database.models import Base

# Налаштування логування
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Встановлюємо URL бази даних з нашого конфігу
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Метадані моделей для Alembic
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск міграцій в 'offline' режимі."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Виконання міграцій всередині синхронного контексту."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Асинхронний запуск міграцій."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск міграцій в 'online' режимі."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
