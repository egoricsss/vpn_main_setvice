from fastapi import APIRouter, Body
from src.schemes.utils import TelegramIdScheme


router = APIRouter(tags=["Auth"])


@router.post("/auth/register")
async def register_user(telegram_id: TelegramIdScheme) -> TelegramIdScheme:
    return telegram_id
