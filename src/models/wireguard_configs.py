from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.dependencies import TimestampMixin
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET


class WireGuardConfigs(Base, TimestampMixin):
    __tablename__ = "wireguard_configs"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    private_key: Mapped[str] = mapped_column(String(44), nullable=False)
    public_key: Mapped[str] = mapped_column(String(44), nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)

    users = relationship("Users", back_populates="wireguard_configs")
