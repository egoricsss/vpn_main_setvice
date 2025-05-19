import json
from src.utils import get_logger
import hashlib
from functools import wraps
from typing import Callable, Optional, ParamSpec, TypeVar, Awaitable
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError, TimeoutError

# Configure logger
logger = get_logger().getChild(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class CacheHelper:
    _pool: Optional[ConnectionPool] = None
    _client: Optional[Redis.connection] = None
    _initialized = False

    @classmethod
    async def connect(cls, url: str, max_connections: int = 10) -> None:
        if cls._initialized:
            logger.warning("Attempted to reconnect to Redis")
            return

        try:
            cls._pool = Redis.from_url(
                url, max_connections=max_connections
            ).connection_pool
            cls._client = Redis(connection_pool=cls._pool)
            cls._initialized = True
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise

    @classmethod
    async def disconnect(cls) -> None:
        if cls._client:
            try:
                await cls._client.aclose()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Failed to close Redis connection: {e}")
            finally:
                cls._client = None
                cls._pool = None
                cls._initialized = False

    @classmethod
    def _generate_key(cls, func_name: str, args: tuple, kwargs: dict) -> str:
        try:
            # Normalize kwargs for stable order
            sorted_kwargs = sorted(kwargs.items())

            # Create hash of arguments for key uniqueness
            args_hash = hashlib.sha256(
                json.dumps((args, sorted_kwargs), default=str).encode()
            ).hexdigest()

            key = f"{func_name}:{args_hash}"
            return key[:200]  # Limit key length (max 200 characters)
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}", exc_info=True)
            raise

    @classmethod
    def cache(
        cls, ttl: int = 3600, prefix: str = "cache"
    ) -> Callable[[Callable[P, T]], Callable[P, Awaitable[T]]]:
        def decorator(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                if not cls._initialized or cls._client is None:
                    logger.warning("Caching unavailable: Redis client not initialized")
                    return await func(*args, **kwargs)

                key = f"{prefix}:{func.__module__}.{func.__name__}"

                try:
                    # Generate unique key
                    key = cls._generate_key(
                        f"{prefix}:{func.__module__}.{func.__name__}", args, kwargs
                    )
                except Exception as e:
                    logger.error(f"Failed to generate cache key: {e}")
                    return await func(*args, **kwargs)

                try:
                    # Try to get data from cache
                    cached_value = await cls._client.get(key)

                    if cached_value is not None:
                        try:
                            data = json.loads(cached_value)
                            logger.debug(f"Cache hit for key: {key}")
                            return data
                        except json.JSONDecodeError as je:
                            logger.error(f"Failed to decode JSON for key {key}: {je}")
                            await cls._client.delete(key)  # Remove corrupted cache

                except (ConnectionError, TimeoutError) as re:
                    logger.error(f"Redis connection error: {re}")
                except RedisError as re:
                    logger.error(f"Redis operation error: {re}")
                except Exception as e:
                    logger.error(
                        f"Unexpected error during Redis operation: {e}", exc_info=True
                    )

                try:
                    # Execute original function
                    result = await func(*args, **kwargs)

                    # Cache result only if not None
                    if result is not None and cls._initialized and cls._client:
                        try:
                            await cls._client.set(
                                name=key,
                                value=json.dumps(result, default=str),
                                ex=ttl,
                            )
                            logger.debug(f"Result cached for key: {key}")
                        except (ConnectionError, TimeoutError) as re:
                            logger.error(f"Redis connection error: {re}")
                        except RedisError as re:
                            logger.error(f"Redis operation error: {re}")
                        except Exception as e:
                            logger.error(
                                f"Unexpected error saving to Redis: {e}", exc_info=True
                            )

                    return result

                except Exception as e:
                    logger.error(
                        f"Error executing function {func.__name__}: {e}", exc_info=True
                    )
                    raise

            return wrapper

        return decorator
