from pydantic import BaseModel
from pydantic.types import SecretStr
from ipaddress import IPv4Network
from typing import Optional


class ConfigModelScheme(BaseModel):
    id: int
    user_id: int
    private_key: SecretStr
    ip_address: IPv4Network


class ConfigInsertScheme(BaseModel):
    user_id: int
    private_key: SecretStr
    ip_address: IPv4Network


class ConfigFilterScheme(BaseModel):
    id: Optional[int]
    user_id: Optional[int]
    private_key: Optional[SecretStr]
    ip_address: Optional[IPv4Network]


class ConfigUpdateScheme(ConfigFilterScheme):
    pass
