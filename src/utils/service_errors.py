from enum import Enum

from fastapi import FastAPI, HTTPException, Request, status
from src.utils import get_logger


logger = get_logger().getChild(__name__)


class TeamResponseStatus(Enum):
    NOT_FOUND = "NOT FOUND"
    FORBIDDEN = "FORBIDDEN"
    MEMBER_NOT_EXIST = "MEMBER IS NOT EXIST"
    INVALID_DATA = "INVALID DATA"
    DATA_FETCH_ERROR = "DATA FETCH ERROR"
    INTERNAL_ERROR = "INTERNAL ERROR"
    DATA_CONFLICT = "DATA_CONFLICT"


STATUS_CODE_MAPPING = {
    TeamResponseStatus.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    TeamResponseStatus.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    TeamResponseStatus.MEMBER_NOT_EXIST: status.HTTP_403_FORBIDDEN,
    TeamResponseStatus.INVALID_DATA: status.HTTP_400_BAD_REQUEST,
    TeamResponseStatus.DATA_FETCH_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
    TeamResponseStatus.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    TeamResponseStatus.DATA_CONFLICT: status.HTTP_409_CONFLICT,
}


class ServiceError(Exception):
    response_status: TeamResponseStatus


class NotFoundError(ServiceError):
    response_status = TeamResponseStatus.NOT_FOUND


class ForbiddenError(ServiceError):
    response_status = TeamResponseStatus.FORBIDDEN


class DataValidationError(ServiceError):
    response_status = TeamResponseStatus.INVALID_DATA


class DataFetchError(ServiceError):
    response_status = TeamResponseStatus.DATA_FETCH_ERROR


class InternalServiceError(ServiceError):
    response_status = TeamResponseStatus.INTERNAL_ERROR


class DataConflictServiceError(ServiceError):
    response_status = TeamResponseStatus.DATA_CONFLICT


def create_exception_handlers(app: FastAPI):

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        code = STATUS_CODE_MAPPING[exc.response_status]
        message = exc.response_status.value
        logger.warning(f"ServiceError: {exc.response_status.value} at {request.url}, code: {code}")
        raise HTTPException(status_code=code, detail=message)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception at {request.url}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=TeamResponseStatus.INTERNAL_ERROR.value,
        )
