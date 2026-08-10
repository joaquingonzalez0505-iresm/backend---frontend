from fastapi import APIRouter
from app.core.config import WELCOME_MESSAGE

router = APIRouter()

@router.get("/")
def welcome():
    return {
        "mensaje": WELCOME_MESSAGE
    }
