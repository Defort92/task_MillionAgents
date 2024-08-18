import os
import shutil
from uuid import uuid4

from fastapi import UploadFile

from app.configs import LOCAL_STORAGE_PATH


def generate_uid() -> str:
    """
    Генерирует уникальный идентификатор (UUID) в виде строки.

    :return: Уникальный идентификатор.
    :rtype: str
    """
    return str(uuid4())


def save_file_locally(file: UploadFile, uid: str) -> str:
    """
    Сохраняет файл локально в указанной директории с уникальным именем.

    :param file: Загружаемый файл.
    :type file: UploadFile
    :param uid: Уникальный идентификатор для файла.
    :type uid: str
    :return: Путь до сохраненного файла.
    :rtype: str
    """
    if not os.path.exists(LOCAL_STORAGE_PATH):
        os.makedirs(LOCAL_STORAGE_PATH)

    file_path = os.path.join(LOCAL_STORAGE_PATH, f"{uid}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
