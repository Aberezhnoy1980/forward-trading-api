import logging
from logging.handlers import RotatingFileHandler
from src.core.config import logging_config


class LoggerFactory:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            from src.core.logsetup import setup_logging
            setup_logging()
            cls._initialized = True

    @classmethod
    def get_logger(cls, name: str, log_file: str | None = None) -> logging.Logger:
        """Получить логгер для конкретного модуля"""
        cls.initialize()

        logger = logging.getLogger(name)

        # Если нужен отдельный файл для этого логгера
        if log_file:
            log_path = logging_config.LOG_DIR / log_file
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=logging_config.MAX_LOG_SIZE * 1024 * 1024,
                backupCount=logging_config.BACKUP_COUNT,
                encoding='utf-8'
            )
            formatter = logging.Formatter(logging_config.LOG_FORMAT)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


# Предопределенные логгеры для разных модулей
def get_email_logger(log_file: str | None = None):
    return LoggerFactory.get_logger("email_service", log_file)


def get_auth_logger(log_file: str | None = None):
    return LoggerFactory.get_logger("auth_service", log_file)


def get_db_logger(log_file: str | None = None):
    return LoggerFactory.get_logger("database", log_file)


def get_app_logger():
    return LoggerFactory.get_logger("app")
