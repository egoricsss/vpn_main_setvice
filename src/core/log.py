import os
import sys

from loguru import logger

from src.core.config.config import LoggingConfig


def setup_logging(mode: str, config: LoggingConfig):
    logger.remove()

    if mode == "TEST":
        if os.path.exists("logs/test.log"):
            os.remove("logs/test.log")

        logger.add(
            "logs/test.log",
            level="DEBUG",
            format=config.FORMAT,
            rotation=config.ROTATION,
            compression=config.COMPRESSION,
            backtrace=config.BACKTRACE,
            serialize=config.SERIALIZE,
        )
    elif mode == "DEV":
        logger.add(
            sys.stdout,
            level="DEBUG",
            format=config.FORMAT,
            backtrace=config.BACKTRACE,
        )

    logger.add(
        "logs/info.log",
        level="INFO",
        format=config.FORMAT,
        rotation=config.ROTATION,
        compression=config.COMPRESSION,
        backtrace=config.BACKTRACE,
        serialize=config.SERIALIZE,
    )

    logger.add(
        "logs/error.log",
        level="ERROR",
        format=config.FORMAT,
        rotation=config.ROTATION,
        compression=config.COMPRESSION,
        backtrace=config.BACKTRACE,
        serialize=config.SERIALIZE,
    )
