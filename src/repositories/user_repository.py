from src.core.database import TypedRepository
from src.models import Users
from src.schemes.users import (
    UserFilterScheme,
    UserModelScheme,
    UserUpdateScheme,
    UserInsertScheme,
)


class UserRepository(
    TypedRepository[
        Users, UserModelScheme, UserInsertScheme, UserFilterScheme, UserUpdateScheme
    ],
    model=Users,
    model_scheme=UserModelScheme,
    insert_scheme=UserInsertScheme,
    filter_scheme=UserFilterScheme,
    update_scheme=UserUpdateScheme,
):
    pass
