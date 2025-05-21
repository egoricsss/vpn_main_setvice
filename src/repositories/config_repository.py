from src.models import WireGuardConfigs
from src.core.database import TypedRepository
from src.schemes.configs import (
    ConfigInsertScheme,
    ConfigFilterScheme,
    ConfigUpdateScheme,
    ConfigModelScheme,
)


class ConfigRepository(
    TypedRepository[
        WireGuardConfigs,
        ConfigModelScheme,
        ConfigInsertScheme,
        ConfigFilterScheme,
        ConfigUpdateScheme,
    ],
    model=WireGuardConfigs,
    model_scheme=ConfigModelScheme,
    insert_scheme=ConfigInsertScheme,
    filter_scheme=ConfigFilterScheme,
    update_scheme=ConfigUpdateScheme,
):
    pass
