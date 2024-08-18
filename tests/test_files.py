import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import FileMetadata


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_module():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_file(setup_module):
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
    assert os.path.exists(file_record.path)
    db.close()


def test_delete_file(setup_module):
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
