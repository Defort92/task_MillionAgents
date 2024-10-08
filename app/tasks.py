import os
import logging

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import get_db
from app.models import FileMetadata as FileModel
from app.cloud_storage import delete_file_from_cloud
from app.configs import LOCAL_STORAGE_PATH, logger


def clean_unused_files() -> None:
    """
    Удаляет неиспользуемые файлы из локального хранилища, которые отсутствуют в базе данных.

    Функция перебирает все файлы в локальном хранилище и удаляет те, которые
    не имеют соответствующей записи в базе данных. Аналогично с файлами на Yandex Cloud Storage

    :return: None
    :rtype: None
    """
    logger.info("Starting cleanup of unused files...")
    db: Session = next(get_db())

    try:
        files_in_db = db.query(FileModel).all()
        files_in_db_paths = {file_record.path for file_record in files_in_db}
        files_in_db_cloud = {
            os.path.basename(file_record.path) for file_record in files_in_db if file_record.storage_url
        }

        for root, dirs, files in os.walk(LOCAL_STORAGE_PATH):
            for filename in files:
                file_path = os.path.join(root, filename)

                if file_path not in files_in_db_paths:
                    logger.info(f"Deleting unused file: {file_path}")

                    os.remove(file_path)

        # Проверяем файлы в облаке Yandex Cloud
        files_in_cloud = list_files_in_cloud()
        for file_name in files_in_cloud:
            if file_name not in files_in_db_cloud:
                logging.info(f"Deleting unused file from Yandex Cloud: {file_name}")
                try:
                    delete_file_from_cloud(file_name)
                    logging.info(f"Deleted {file_name} from Yandex Cloud")
                except Exception as e:
                    logging.error(f"Failed to delete {file_name} from Yandex Cloud: {e}")

        logger.info("Cleanup completed successfully.")
    except Exception as e:
        logger.error(f"Failed to clean unused files: {e}")
    finally:
        db.close()


def start_scheduler() -> None:
    """
    Запускает планировщик задач для регулярной очистки неиспользуемых файлов.

    Планировщик настроен на выполнение задачи по очистке файлов каждый день в 01:00.

    :return: None
    :rtype: None
    """
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=1, minute=0)
    scheduler.add_job(clean_unused_files, trigger)
    scheduler.start()
    logger.info("Scheduler started.")
