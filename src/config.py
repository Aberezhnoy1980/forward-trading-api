from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    USERS_DB_HOST: str
    USERS_DB_PORT: int
    USERS_DB_USER: str
    USERS_DB_PASS: str
    USERS_DB_NAME: str

    @property
    def USERS_DB_URL(self):
        return (
            f"postgresql+asyncpg://{self.USERS_DB_USER}:{self.USERS_DB_PASS}@{self.USERS_DB_HOST}:{self.USERS_DB_PORT}/{self.USERS_DB_NAME}")

    DOMAIN: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
