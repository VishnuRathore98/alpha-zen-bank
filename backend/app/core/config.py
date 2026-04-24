from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT = Literal["local", "staging", "production"] = "local"

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file="../../.envs/.env.local",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    API_V1_STR: str = ""
    SITE_NAME: str = ""


settings = Settings()
