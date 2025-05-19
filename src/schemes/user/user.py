from pydantic import BaseModel
from typing import Optional


class UserModelScheme(BaseModel):
    id: int
    telegram_id: int
    is_active: bool


class UserInsertScheme(UserModelScheme):
    is_active: bool = False


class UserFilterScheme(BaseModel):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserUpdateScheme(UserFilterScheme):
    pass
