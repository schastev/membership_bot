from typing import List

from aiogram.types import KeyboardButton

from config_reader import config
from src.utils.db_user import check_admin, check_user_registration_state, check_no_memberships
from translation import t

_ = t.gettext

def main_buttons(user_id: int) -> list:
    menu_buttons = []
    user_is_registered = check_user_registration_state(user_id)
    user_is_admin = check_admin(user_id)
    user_has_no_memberships = check_no_memberships(user_id)
    if user_is_admin:
        menu_buttons.append(KeyboardButton(text=_("manage_button")))
    if user_is_registered and user_has_no_memberships:
        menu_buttons.append(KeyboardButton(text=_("add_membership")))
    elif user_is_registered and not user_has_no_memberships:
        menu_buttons.append(KeyboardButton(text=_("view_membership_button")))
    if user_is_registered:
        menu_buttons.extend(
            [KeyboardButton(text=_("change_name_button")), KeyboardButton(text=_("change_phone_button"))]
        )
    else:
        menu_buttons.append(KeyboardButton(text=_("register_button")))
    return menu_buttons


def membership_request_buttons(request_list: List[dict]) -> list:
    menu_buttons = []
    for request in request_list:
        menu_buttons.append(KeyboardButton(text=f'{request["member"].name}: {int(request["member"].phone)}'))
    return menu_buttons


def membership_value_buttons() -> list:
    menu_buttons = []
    membership_values = config.membership_values
    for value in membership_values:
        menu_buttons.append(KeyboardButton(text=str(value)))
    menu_buttons.append(KeyboardButton(text=_("decline")))
    return menu_buttons
