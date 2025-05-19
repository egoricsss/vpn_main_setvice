from pydantic import BaseModel, field_serializer
from src.models import PaymentStatus, PaymentMethod
from decimal import Decimal
from typing import Optional


class _PaymentBaseScheme(BaseModel):
    @field_serializer("status")
    def serialize_status(self, status: Optional[PaymentStatus]):
        return status.value if status else None

    @field_serializer("payment_method")
    def serialize_payment_method(self, method: Optional[PaymentMethod]):
        return method.value if method else None


class PaymentModelScheme(_PaymentBaseScheme):
    id: int
    user_id: int
    status: PaymentStatus
    payment_method: PaymentMethod
    amount: Decimal


class PaymentInsertScheme(_PaymentBaseScheme):
    user_id: int
    status: PaymentStatus = PaymentStatus.unpaid
    payment_method: PaymentMethod
    amount: Decimal


class PaymentFilterScheme(_PaymentBaseScheme):
    id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    amount: Optional[Decimal] = None


class PaymentUpdateScheme(_PaymentBaseScheme):
    pass
