import logging
import sys


def setup_logging(worker_queue_name: str):
    """
    Настраивает глобальное логирование для приложения.
    """
    # Формат логов: Время | Уровень | Воркер | Модуль | Сообщение
    log_format = f"%(asctime)s | %(levelname)-8s | [{worker_queue_name}] | %(name)s | %(message)s"

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)

    logging.getLogger("temporalio").setLevel(logging.INFO)
    logging.getLogger("temporalio.core").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
