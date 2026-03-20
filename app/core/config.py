# config.py is the file that uses pydantic-settings to read that
# .env file and make all those values available throughout your entire application.

# A Settings class that does three things:
# 1. reads every variable from your .env file
# 2. validates them — wrong type throws an error immediately
# 3. makes them available anywhere in your app via one import
# 4. when an env variablename typo is made, is fails loud

# .env file  →  config.py (pydantic-settings reads + validates)  →  any file that needs it



from pydantic_settings import BaseSettings
# Pydantic type that validates a string is a properly formatted URL. We use it for CORS origins.
# from pydantic import AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    # application
    app_name: str = "Syncflow"
    app_version: str = "0.1.0"
    debug: bool = True

    # security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # database
    database_url: str

    # redis
    redis_url: str

    # cors
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()