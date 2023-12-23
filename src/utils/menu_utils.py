
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
    elif not user_is_registered:
        menu_buttons.append(KeyboardButton(text=locale.register_button))
    elif user_is_registered:
        menu_buttons.extend(
            [
                KeyboardButton(text=locale.change_name_button),
                KeyboardButton(text=locale.change_phone_button),
                KeyboardButton(text=locale.view_memberships_button),
            ]
        )
    return menu_buttons
