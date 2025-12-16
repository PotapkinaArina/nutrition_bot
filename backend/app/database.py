from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# Создаём engine для подключения к PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,          # лог SQL-запросов (удобно для отладки)
    future=True
)

# Фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Базовый класс для моделей
Base = declarative_base()
