import os
import shutil
from uuid import uuid4

from app.configs import LOCAL_STORAGE_PATH


def generate_uid():
    return str(uuid4())


def save_file_locally(file, uid):
    if not os.path.exists(LOCAL_STORAGE_PATH):
        os.makedirs(LOCAL_STORAGE_PATH)

    file_path = os.path.join(LOCAL_STORAGE_PATH, f"{uid}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
