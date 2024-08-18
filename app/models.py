from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    original_name = Column(String, index=True)
    size = Column(Integer)
    content_type = Column(String)
    path = Column(String)
    storage_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
