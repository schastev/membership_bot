from random import Random
from typing import List

from aiogram_tests.types.dataset import USER, CHAT


def extract_keyboard_entries(keyboard) -> List[str]:
    result = []
    [result.extend(r) for r in keyboard]
    return [button.text.replace("_button", "") for button in result]


def get_random_locale() -> str:
    # return Random().choice(config_reader.config.locales)
    return "ru"  # todo fix en this working as ru


def get_user(with_membership: bool, locale: str):
    from src.db_calls.admin import add_membership
    from src.db_calls.member import request_to_add_membership, get_active_membership_by_user_id
    from src.db_calls.user import register_user

    user_id = Random().randint(0, 999999999)
    user = register_user(tg_id=user_id, name=USER.get("username"), phone=str(user_id), locale=locale)
    membership = None
    if with_membership:
        request = request_to_add_membership(tg_id=user.tg_id, chat_id=CHAT.get("id"))
        add_membership(tg_id=user.tg_id, membership_value=10, request_id=request.id)
        membership = get_active_membership_by_user_id(tg_id=user.tg_id)
    return user, membership
