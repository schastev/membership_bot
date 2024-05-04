from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import pathlib


class Settings(BaseSettings, extra="allow"):
    bot_token: SecretStr
    model_config = SettingsConfigDict(
        env_file=pathlib.Path(__file__).parent / ".env", env_file_encoding="utf-8"
    )
    admin_ids: List[int]
    membership_values: List[int]
    polling_timeout_seconds: int
    locales: List[str]
    membership_duration_days: int
    max_freeze_duration: int
    database_file_name: str


config = Settings()
