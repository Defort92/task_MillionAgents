import os
import logging

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import get_db
from app.models import FileMetadata as FileModel
from app.cloud_storage import delete_file_from_cloud
from app.configs import LOCAL_STORAGE_PATH, logger


def clean_unused_files():
    logger.info("Starting cleanup of unused files...")
    db: Session = next(get_db())

    try:
        files_in_db = db.query(FileModel).all()
        files_in_db_paths = {file_record.path for file_record in files_in_db}

        for root, dirs, files in os.walk(LOCAL_STORAGE_PATH):
            for filename in files:
                file_path = os.path.join(root, filename)

                if file_path not in files_in_db_paths:
                    logger.info(f"Deleting unused file: {file_path}")

                    os.remove(file_path)

        logger.info("Cleanup completed successfully.")
    except Exception as e:
        logger.error(f"Failed to clean unused files: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=1, minute=0)
    scheduler.add_job(clean_unused_files, trigger)
    scheduler.start()
    logger.info("Scheduler started.")
