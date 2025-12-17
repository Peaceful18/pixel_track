from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app_config.config import settings  # <--- Імпортуємо наш клас налаштувань

from .models import Base

# Більше ніяких os.getenv тут!
# Ми беремо готовий URL, який зібрав клас Settings
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Ініціалізація бази даних, створення таблиць."""
    print(
        f"Connecting to DB at: {settings.DB_HOST}:{settings.DB_PORT}"
    )  # Можна додати лог для налагодження
    print("Ініціалізація бази даних...")
    Base.metadata.create_all(bind=engine)
    print("База даних ініціалізована.")


# Ця функція знадобиться тобі для FastAPI (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
