from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class FileMetadata(Base):
    """
    Модель для хранения метаданных файлов в базе данных.

    Атрибуты:
        id: Уникальный идентификатор записи.
        uid: Уникальный идентификатор файла.
        original_name: Оригинальное имя файла.
        size: Размер файла в байтах.
        content_type: MIME-тип файла.
        path: Локальный путь до файла.
        storage_url: URL файла в облачном хранилище.
        created_at: Дата и время создания записи.
    """
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    original_name = Column(String, index=True)
    size = Column(Integer)
    content_type = Column(String)
    path = Column(String)
    storage_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
