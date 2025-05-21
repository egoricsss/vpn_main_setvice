from pydantic import BaseModel


class TelegramIdScheme(BaseModel):
    telegram_id: int
