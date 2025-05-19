from abc import ABC, abstractmethod
from datetime import datetime
from inspect import currentframe
from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped


class Base(DeclarativeBase):
    pass


class RepositoryABC(ABC):
    @abstractmethod
    async def get_one(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def insert(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def insert_or_ignore(self, data: dict[str, Any]) -> Any:
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)


class SqlAlchemyRepository(RepositoryABC):
    _model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert(self, data: dict[str, Any]) -> dict[str, Any] | None:
        stmt = insert(self._model).values(**data).returning(self._model)
        res = await self._session.execute(stmt)
        row = res.scalar_one()
        return row

    async def insert_or_ignore(self, data: dict[str, Any]) -> dict[str, Any] | None:
        stmt = (
            insert(self._model)
            .values(**data)
            .on_conflict_do_nothing()
            .returning(self._model)
        )
        res = await self._session.execute(stmt)
        if row := res.scalar_one_or_none():
            return row
        return None

    async def get_one(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        stmt = select(self._model).filter_by(**filters)
        res = await self._session.execute(stmt)
        if row := res.scalar_one_or_none():
            return row
        return None

    async def get_all(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        stmt = select(self._model).filter_by(**filters)
        res = await self._session.execute(stmt)
        return [row for row in res.scalars()]

    async def update(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        data["updated_at"] = datetime.now()
        stmt = (
            update(self._model)
            .filter_by(**filters)
            .values(**data)
            .returning(self._model)
        )
        res = await self._session.execute(stmt)
        if row := res.scalar_one_or_none():
            return row
        return None

    async def delete(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        stmt = delete(self._model).filter_by(**filters).returning(self._model)
        res = await self._session.execute(stmt)
        if row := res.scalar_one_or_none():
            return row
        return None


class RepositoryValidationError(ValueError):
    def __init__(self, method: str, data: Any, errors: list, direction: str):
        self.method = method
        self.data = data
        self.errors = errors
        self.direction = direction  # 'input' или 'output'
        error_details = "\n".join([f"{e['loc']}: {e['msg']}" for e in errors])
        super().__init__(
            f"Validation failed in {method} ({direction}):\n"
            f"Data: {self._safe_repr(data)}\n"
            f"Errors:\n{error_details}"
        )

    @staticmethod
    def _safe_repr(data: Any) -> str:
        if isinstance(data, dict):
            return repr(
                {k: "***MASKED***" if "password" in k else v for k, v in data.items()}
            )
        return repr(data)


ModelSchemeType = TypeVar("ModelSchemeType", bound=BaseModel)
InsertSchemeType = TypeVar("InsertSchemeType", bound=BaseModel)
FilterSchemeType = TypeVar("FilterSchemeType", bound=BaseModel)
UpdateSchemeType = TypeVar("UpdateSchemeType", bound=BaseModel)


class TypedRepository(
    SqlAlchemyRepository,
    Generic[
        ModelType, ModelSchemeType, InsertSchemeType, FilterSchemeType, UpdateSchemeType
    ],
):
    _model: Type[ModelType]
    _model_scheme: Type[ModelSchemeType]
    _insert_scheme: Type[InsertSchemeType]
    _filter_scheme: Type[FilterSchemeType]
    _update_scheme: Type[UpdateSchemeType]

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def __init_subclass__(cls, **kwargs):
        required_kwargs = [
            "model",
            "model_scheme",
            "insert_scheme",
            "filter_scheme",
            "update_scheme",
        ]
        missing = [kw for kw in required_kwargs if kw not in kwargs]
        if missing:
            raise AttributeError(f"'{cls.__name__}' must define {', '.join(missing)}.")

        cls._model = kwargs.pop("model")
        cls._model_scheme = kwargs.pop("model_scheme")
        cls._insert_scheme = kwargs.pop("insert_scheme")
        cls._filter_scheme = kwargs.pop("filter_scheme")
        cls._update_scheme = kwargs.pop("update_scheme")
        super().__init_subclass__(**kwargs)

    @classmethod
    def _get_caller_method(cls) -> str:
        frame = currentframe().f_back.f_back
        return frame.f_code.co_name if frame else "unknown_method"

    @classmethod
    def _validate_input(
        cls, data: dict[str, Any] | Type[BaseModel], scheme: Type[BaseModel]
    ) -> dict[str, Any]:
        method = cls._get_caller_method()
        try:
            # if we pass PydanticScheme in methods bellow,
            # we return data back
            if isinstance(data, scheme):
                return data.model_dump(exclude_none=True)
            return scheme(**data).model_dump(exclude_none=True)
        except ValidationError as exc:
            raise RepositoryValidationError(
                method=method, data=data, errors=exc.errors(), direction="input"
            ) from exc

    @classmethod
    def _validate_output(
        cls, data: dict[str, Any] | ModelType, scheme: Type[BaseModel]
    ) -> BaseModel:
        method = cls._get_caller_method()
        try:
            return scheme.model_validate(data, from_attributes=True)
        except ValidationError as exc:
            raise RepositoryValidationError(
                method=method, data=data, errors=exc.errors(), direction="output"
            ) from exc

    async def insert(self, data: dict[str, Any] | InsertSchemeType) -> ModelSchemeType:
        validated_data = self._validate_input(data, self._insert_scheme)
        result = await super().insert(validated_data)
        return self._validate_output(result, self._model_scheme)

    async def insert_or_ignore(
        self, data: dict[str, Any] | InsertSchemeType
    ) -> Optional[ModelSchemeType]:
        validated_data = self._validate_input(data, self._insert_scheme)
        result = await super().insert_or_ignore(validated_data)
        if result:
            return self._validate_output(result, self._model_scheme)
        return None

    async def get_one(
        self, filters: dict[str, Any] | FilterSchemeType
    ) -> Optional[ModelSchemeType]:
        validated_filters = self._validate_input(filters, self._filter_scheme)
        result = await super().get_one(validated_filters)
        if result:
            return self._validate_output(result, self._model_scheme)
        return None

    async def get_all(
        self, filters: dict[str, Any] | FilterSchemeType
    ) -> list[ModelSchemeType]:
        validated_filters = self._validate_input(filters, self._filter_scheme)
        results = await super().get_all(validated_filters)
        return [self._validate_output(r, self._model_scheme) for r in results]

    async def update(
        self,
        filters: dict[str, Any] | FilterSchemeType,
        data: dict[str, Any] | UpdateSchemeType,
    ) -> Optional[ModelSchemeType]:
        validated_filters = self._validate_input(filters, self._filter_scheme)
        validated_data = self._validate_input(data, self._update_scheme)
        result = await super().update(validated_filters, validated_data)
        if result:
            return self._validate_output(result, self._model_scheme)
        return None

    async def delete(
        self, filters: dict[str, Any] | FilterSchemeType
    ) -> Optional[ModelSchemeType]:
        validated_filters = self._validate_input(filters, self._filter_scheme)
        result = await super().delete(validated_filters)
        if result:
            return self._validate_output(result, self._model_scheme)
        return None
