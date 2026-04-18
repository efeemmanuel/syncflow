from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_url: Optional[str] = None
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()