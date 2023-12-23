from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Extra


class Settings(BaseSettings, extra=Extra.allow):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    admin_ids: List[int]
    membership_values: List[int]


config = Settings()
