from fastapi import FastAPI
from app.core.config import PROJECT_NAME, PROJECT_VERSION
from app.routers import welcome

app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION
)

app.include_router(welcome.router)
