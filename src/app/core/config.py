from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, can be loaded from .env file
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "mysql+pymysql://superRoot:Mat90017@mat90017.mysql.database.azure.com:3306/mat90017"

    # Session Settings
    SECRET_KEY: str = "my_secret_key"
    SESSION_EXPIRE_MINUTES: int = 30

settings = Settings()
