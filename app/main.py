from fastapi import FastAPI

from app.routers import files
from app.database import engine, Base
from app.tasks import start_scheduler


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(files.router)

start_scheduler()
