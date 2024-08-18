import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.configs import DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Создает и предоставляет сессию базы данных для выполнения запросов.

    Функция используется для создания и закрытия сессии SQLAlchemy при каждом обращении.
    Она возвращает сессию через генератор.

    :yield: Сессия базы данных SQLAlchemy.
    :rtype: Generator[Session, None, None]
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
