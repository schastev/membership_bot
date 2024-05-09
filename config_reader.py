from pathlib import Path
from typing import List

from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import pathlib

from src.utils.decorators import singleton


class ProdSettings(BaseSettings, extra="allow"):
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


class TestSettings(BaseSettings, extra="allow"):
    bot_token: SecretStr
    admin_ids: List[int]
    membership_values: List[int]
    polling_timeout_seconds: int
    locales: List[str]
    membership_duration_days: int
    max_freeze_duration: int
    database_file_name: str


@singleton
class GlobalSettings:
    config: BaseSettings | None = None
    i18n: I18n | None = None
    locale: FSMI18nMiddleware | None = None

    def __init__(self, prod_env: bool = False):
        if prod_env:
            self.config = ProdSettings()
        else:
            self.config = TestSettings(
                bot_token="",
                admin_ids=[123],
                membership_values=[2, 4, 6],
                polling_timeout_seconds=3,
                locales=["en", "ru"],
                membership_duration_days=10,
                max_freeze_duration=14,
                database_file_name="",
                company_name="Test",
            )
        self.i18n = I18n(
            path=Path(__file__).resolve().parent / "src" / "locales",
            domain="mb_bot",
        )
        self.locale = FSMI18nMiddleware(i18n=self.i18n)
