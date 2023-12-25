from typing import Any

from aiogram.types import ReplyKeyboardMarkup

from src.utils.menu import main_buttons


class FullMenuMarkup(ReplyKeyboardMarkup):
    def __init__(self, *, user_id: id, **__pydantic_kwargs: Any):
        keyboard = main_buttons(user_id=user_id)
        super().__init__(keyboard=[keyboard], resize_keyboard=True, **__pydantic_kwargs)
