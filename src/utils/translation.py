from pathlib import Path

from aiogram.utils.i18n import I18n, FSMI18nMiddleware

import config_reader

i18n = I18n(
    path=Path(__file__).resolve().parent.parent.parent / "src" / "locales",
    default_locale=config_reader.config.default_locale,
    domain="mb_bot"
)
locale = FSMI18nMiddleware(i18n=i18n)
