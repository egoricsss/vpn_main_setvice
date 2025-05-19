import glob
import logging
import os
import queue
from logging.handlers import QueueHandler, QueueListener
from src.core.config import config


def clear_logs_folder(log_dir="logs", pattern="bot.log*"):
    try:
        if os.path.exists(log_dir):
            log_files = glob.glob(os.path.join(log_dir, pattern))
            for f in log_files:
                os.remove(f)
                logging.info(f"🤗 Удалён файл: {f}")
        else:
            logging.info(f"🐻 Папка {log_dir} не найдена")
    except Exception as e:
        logging.info(f"❌ Ошибка при очистке логов: {e}")


os.makedirs("logs", exist_ok=True)
log_queue = queue.Queue()

formatter = logging.Formatter(fmt=config.log.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger("MainServiceLogger")
logger.setLevel(logging.DEBUG)

if config.api.MODE == "TEST":
    clear_logs_folder()

file_handler = logging.FileHandler("logs/service.log")
file_handler.setFormatter(formatter)

queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)

queue_listener = QueueListener(
    log_queue, file_handler, console_handler, respect_handler_level=True
)
queue_listener.start()

logger.debug("✅ Logging is ready for work")


def get_logger() -> logging.Logger:
    return logger
