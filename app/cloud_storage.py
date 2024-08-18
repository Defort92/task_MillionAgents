import os

from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

from app.configs import (
    YANDEX_CLOUD_ACCESS_KEY,
    YANDEX_CLOUD_SECRET_KEY,
    YANDEX_CLOUD_BUCKET_NAME,
    YANDEX_CLOUD_ENDPOINT_URL,
)


s3_client = boto3.client(
    "s3",
    endpoint_url=YANDEX_CLOUD_ENDPOINT_URL,
    aws_access_key_id=YANDEX_CLOUD_ACCESS_KEY,
    aws_secret_access_key=YANDEX_CLOUD_SECRET_KEY
)


def upload_file_to_cloud(file_path: str, file_name: str) -> str:
    """
    Загружает файл в Yandex Cloud Object Storage.

    :param file_path: Путь до файла на локальном диске.
    :type file_path: str
    :param file_name: Имя файла для сохранения в облаке.
    :type file_name: str
    :return: URL загруженного файла в облаке.
    :rtype: str
    :raises Exception: Если произошла ошибка при загрузке файла.
    """
    try:
        s3_client.upload_file(file_path, YANDEX_CLOUD_BUCKET_NAME, file_name)
        file_url = f"{YANDEX_CLOUD_ENDPOINT_URL}/{YANDEX_CLOUD_BUCKET_NAME}/{file_name}"
        return file_url
    except FileNotFoundError:
        raise Exception("The file was not found")
    except NoCredentialsError:
        raise Exception("Credentials not available")
    except ClientError as e:
        raise Exception(f"Failed to upload to Yandex Cloud: {e}")


def delete_file_from_cloud(file_name: str) -> None:
    """
    Удаляет файл из Yandex Cloud Object Storage.

    :param file_name: Имя файла в облаке.
    :type file_name: str
    :return: None
    :rtype: None
    :raises Exception: Если произошла ошибка при удалении файла.
    """
    try:
        s3_client.delete_object(Bucket=YANDEX_CLOUD_BUCKET_NAME, Key=file_name)
    except ClientError as e:
        raise Exception(f"Failed to delete file from Yandex Cloud: {e}")


async def upload_to_cloud_and_update_db(local_file_path: str, file_record, db: Session) -> None:
    """
    Загружает файл в облако и обновляет запись в базе данных.

    :param local_file_path: Путь до файла на локальном диске.
    :type local_file_path: str
    :param file_record: Запись файла в базе данных.
    :type file_record: FileMetadata
    :param db: Сессия базы данных.
    :type db: Session
    :return: None
    :rtype: None
    """
    file_url = upload_file_to_cloud(local_file_path, os.path.basename(local_file_path))

    file_record.storage_url = file_url
    db.add(file_record)
    db.commit()
