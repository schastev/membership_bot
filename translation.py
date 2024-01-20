from pathlib import Path

from aiogram.utils.i18n import I18n, FSMI18nMiddleware


i18n = I18n(path=Path(__file__).resolve().parent / "src" / "locales", default_locale="en", domain="mb_bot")
locale = FSMI18nMiddleware(i18n=i18n)