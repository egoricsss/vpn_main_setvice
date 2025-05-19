from functools import wraps

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.utils import get_logger, ServiceError, InternalServiceError


logger = get_logger().getChild(__name__)


class BaseService:
    def __init__(self, uow: ...):
        self._uow = uow

    @staticmethod
    def handle_exceptions(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            service_name = args[0].__class__.__name__
            try:
                return await func(*args, **kwargs)
            except ServiceError as service_error:
                logger.error(
                    f"Service error in {service_name}.{func.__name__}: {service_error.response_status.value}, params: {kwargs}"
                )
                raise service_error
            except ValidationError as validation_error:
                logger.error(
                    f"Validating error in {service_name}.{func.__name__}: {validation_error}, params: {kwargs}"
                )
                raise validation_error
            except SQLAlchemyError as db_error:
                logger.error(
                    f"SQLAlchemy error in {service_name}.{func.__name__}: {db_error}, params: {kwargs}"
                )
                raise InternalServiceError
            except Exception as unexpected_error:
                logger.error(
                    f"Unexpected error in {service_name}.{func.__name__}: {unexpected_error}, params: {kwargs}"
                )
                raise InternalServiceError

        return wrapper
