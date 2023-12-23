from typing import List

from config_reader import config
from src.utils.user_actions import check_admin, check_user_registration_state
from aiogram.types import KeyboardButton
locale = config


def compile_main_menu(user_id: int) -> list:
    menu_buttons = []
    user_is_registered = check_user_registration_state(user_id)
    user_is_admin = check_admin(user_id)
    if user_is_admin:
        menu_buttons.append(KeyboardButton(text=locale.manage_button))
    elif user_is_registered:
        menu_buttons.extend(
            [
                KeyboardButton(text=locale.change_name_button),
                KeyboardButton(text=locale.change_phone_button),
                KeyboardButton(text=locale.view_membership_button),
                KeyboardButton(text=locale.add_membership),
            ]
        )
    else:
        menu_buttons.append(KeyboardButton(text=locale.register_button))
    return menu_buttons


def compile_membership_request_list_menu(request_list: List[dict]) -> list:
    menu_buttons = []
    for request in request_list:
        menu_buttons.append(KeyboardButton(text=f'{request["name"]}: {request["phone"]}'))
    return menu_buttons


def compile_membership_value_list_menu() -> list:
    menu_buttons = []
    membership_values = config.membership_values
    for value in membership_values:
        menu_buttons.append(KeyboardButton(text=str(value)))
    return menu_buttons
