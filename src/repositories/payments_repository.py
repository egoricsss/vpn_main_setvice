from src.core.database import TypedRepository
from src.models import Payments
from src.schemes.payments import (
    PaymentModelScheme,
    PaymentUpdateScheme,
    PaymentInsertScheme,
    PaymentFilterScheme,
)


class PaymentRepository(
    TypedRepository[
        Payments,
        PaymentModelScheme,
        PaymentInsertScheme,
        PaymentFilterScheme,
        PaymentUpdateScheme,
    ],
    model=Payments,
    model_scheme=PaymentModelScheme,
    insert_scheme=PaymentInsertScheme,
    filter_scheme=PaymentFilterScheme,
    update_scheme=PaymentUpdateScheme
):
    pass
