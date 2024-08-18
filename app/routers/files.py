import os

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FileMetadata as FileModel
from app.utils import save_file_locally, generate_uid
from app.cloud_storage import delete_file_from_cloud, upload_to_cloud_and_update_db


router = APIRouter(
    prefix="/files",
    tags=["files"]
)

LOCAL_STORAGE_PATH = "storage/"


@router.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    uid = generate_uid()

    local_file_path = save_file_locally(file, uid)

    file_record = FileModel(
        uid=uid,
        original_name=file.filename,
        size=file.size,
        content_type=file.content_type,
        path=local_file_path,
        storage_url=None
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    background_tasks.add_task(upload_to_cloud_and_update_db, local_file_path, file_record, db)

    return {
        "uid": uid,
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type
    }


@router.get("/{uid}")
async def get_file(uid: str, db: Session = Depends(get_db)):
    file_record = db.query(FileModel).filter(FileModel.uid == uid).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(LOCAL_STORAGE_PATH, f"{uid}_{file_record.original_name}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return {"message": f"File {file_record.original_name} is available"}


@router.delete("/{uid}")
async def delete_file(uid: str, db: Session = Depends(get_db)):
    file_record = db.query(FileModel).filter(FileModel.uid == uid).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.exists(file_record.path):
        os.remove(file_record.path)

    if file_record.storage_url:
        delete_file_from_cloud(os.path.basename(file_record.path))

    db.delete(file_record)
    db.commit()

    return {"message": "File deleted successfully"}
