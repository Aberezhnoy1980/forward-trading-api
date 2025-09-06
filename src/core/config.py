from pathlib import Path
from pydantic_settings import BaseSettings


class LoggingConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    LOG_FILE: str = "app.log"
    ERROR_FILE: str = "errors.log"
    MAX_LOG_SIZE: int = 10  # MB
    BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_prefix = "LOG_"


logging_config = LoggingConfig()
