from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

YANDEX_CLOUD_ACCESS_KEY = os.getenv("YANDEX_CLOUD_ACCESS_KEY")
YANDEX_CLOUD_SECRET_KEY = os.getenv("YANDEX_CLOUD_SECRET_KEY")
YANDEX_CLOUD_BUCKET_NAME = os.getenv("YANDEX_CLOUD_BUCKET_NAME")
YANDEX_CLOUD_ENDPOINT_URL = os.getenv("YANDEX_CLOUD_ENDPOINT_URL", "https://storage.yandexcloud.net")

LOCAL_STORAGE_PATH = "storage/"
LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger = logging.getLogger("file_logger")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"), maxBytes=5 * 1024 * 1024, backupCount=5
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
