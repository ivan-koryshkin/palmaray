import ssl
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_SSL: bool
    TG_TOKEN: str
    OPENAI_API_KEY: str
    SECRET_KEY: str
    REDIS_URL: str

    def get_db_str(self) -> str:
        user = quote_plus(self.DB_USER)
        pwd = quote_plus(self.DB_PASS)
        host = self.DB_HOST or "localhost"
        port = self.DB_PORT or 5432
        db = self.DB_NAME
        url = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"
        return url

    def build_connect_args(self) -> dict:
        if self.DB_SSL:
            return {"ssl": ssl.create_default_context()}
        return {"ssl": False}


settings = Settings()  # type: ignore[call-arg]
