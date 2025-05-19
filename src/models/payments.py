from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Enum as SQLAlchemyEnum, ForeignKey, Numeric
from enum import Enum

from src.core.database import Base
from src.core.dependencies import TimestampMixin


class PaymentStatus(str, Enum):
    paid = "PAID"
    unpaid = "UNPAID"


class PaymentMethod(str, Enum):
    telegram_stars = "telegram stars"
    bitcoin = "bitcoin"
    sbp = "sbp"
    card = "card"


class Payments(Base, TimestampMixin):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLAlchemyEnum(PaymentStatus),
        default=PaymentStatus.unpaid,
        nullable=False,
        index=True,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLAlchemyEnum(PaymentMethod), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    user = relationship("Users", back_populates="payments")
