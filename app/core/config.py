from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    redis_host: str
    redis_port: int
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()