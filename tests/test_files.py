import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database import Base, get_db
from app.models import FileMetadata
from app.configs import LOCAL_STORAGE_PATH


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


def override_get_db():
    """
    Переопределение зависимости базы данных для тестов, чтобы использовать тестовую базу данных SQLite.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Подключаем pytest-asyncio для поддержки асинхронных тестов
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def setup_module():
    """
    Фикстура для настройки и очистки базы данных.

    Создает все таблицы перед выполнением тестов и удаляет их после завершения тестов.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def temp_dir():
    """
    Фикстура для создания временной директории для хранения файлов во время тестов.

    Эта фикстура автоматически выполняется перед каждым тестом и очищает временную директорию после выполнения.
    """
    with tempfile.TemporaryDirectory() as temp_directory:
        original_storage_path = LOCAL_STORAGE_PATH
        os.environ['LOCAL_STORAGE_PATH'] = temp_directory
        yield
        os.environ['LOCAL_STORAGE_PATH'] = original_storage_path


async def test_create_file(setup_module):
    """
    Тест загрузки файла через API.

    Этот тест проверяет:
    1. Успешную загрузку файла.
    2. Корректность ответа API, включая наличие уникального идентификатора (UID).
    3. Создание записи о файле в базе данных.
    4. Наличие файла на диске и его корректное содержимое.
    """
    file_content = b"test content"
    response = client.post("/files/upload", files={"file": ("test_file.txt", file_content)})

    assert response.status_code == 200
    data = response.json()
    assert "uid" in data
    assert data["filename"] == "test_file.txt"

    db = TestingSessionLocal()
    file_record = db.query(FileMetadata).filter(FileMetadata.uid == data["uid"]).first()

    assert file_record is not None
    assert file_record.original_name == "test_file.txt"

    with open(file_record.path, "rb") as f:
        assert f.read() == file_content

    db.close()


async def test_delete_file(setup_module):
    """
    Тест удаления файла через API.

    Этот тест проверяет:
    1. Успешную загрузку файла.
    2. Наличие записи о файле в базе данных и файла на диске.
    3. Успешное удаление файла через API.
    4. Удаление записи о файле из базы данных и отсутствие файла на диске после удаления.
    """
    file_content = b"delete me"
    response = client.post("/files/upload", files={"file": ("delete_test.txt", file_content)})

    assert response.status_code == 200
    data = response.json()
    uid = data["uid"]

    db = TestingSessionLocal()
    file_record = db.query(FileMetadata).filter(FileMetadata.uid == uid).first()
    assert file_record is not None
    file_path = file_record.path
    assert os.path.exists(file_path)
    db.close()

    delete_response = client.delete(f"/files/{uid}")
    assert delete_response.status_code == 200

    db = TestingSessionLocal()
    file_record = db.query(FileMetadata).filter(FileMetadata.uid == uid).first()
    assert file_record is None

    assert not os.path.exists(file_path)
    db.close()
