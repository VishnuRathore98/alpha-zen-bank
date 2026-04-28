import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


print("BASE_DIR: ", BASE_DIR)


class Settings(BaseSettings):
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=BASE_DIR + "/.envs/.env.local",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    API_V1_STR: str = ""
    SITE_NAME: str = ""

    DATABASE_URL: str = ""


settings = Settings()
