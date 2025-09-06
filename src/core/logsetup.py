import logging
import sys
from logging.handlers import RotatingFileHandler
from src.core.config import logging_config


def setup_logging():
    """Инициализация системы логирования"""

    # Создаем директорию для логов
    logging_config.LOG_DIR.mkdir(exist_ok=True, parents=True)

    # Форматтер
    formatter = logging.Formatter(logging_config.LOG_FORMAT)

    # Уровень логирования
    log_level = getattr(logging, logging_config.LOG_LEVEL.upper())

    # Основной обработчик для всех логов
    main_handler = RotatingFileHandler(
        logging_config.LOG_DIR / logging_config.LOG_FILE,
        maxBytes=logging_config.MAX_LOG_SIZE * 1024 * 1024,
        backupCount=logging_config.BACKUP_COUNT,
        encoding='utf-8'
    )
    main_handler.setFormatter(formatter)
    main_handler.setLevel(log_level)

    # Обработчик для ошибок
    error_handler = RotatingFileHandler(
        logging_config.LOG_DIR / logging_config.ERROR_FILE,
        maxBytes=logging_config.MAX_LOG_SIZE * 1024 * 1024,
        backupCount=logging_config.BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Настройка root логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Уменьшаем логирование сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return root_logger
