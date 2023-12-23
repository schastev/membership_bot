
from config_reader import config
from src.utils.user_actions import check_admin, check_user_registration_state
from aiogram.types import Message, KeyboardButton
locale = config


def compile_menu(message: Message) -> list:
    menu_buttons = []
    if check_admin(message.from_user.id):
        menu_buttons.append(KeyboardButton(text=locale.manage_button))
    elif not check_user_registration_state(message.from_user.id):
        menu_buttons.append(KeyboardButton(text=locale.register_button))
    menu_buttons.extend(
        [KeyboardButton(text=locale.change_name_button), KeyboardButton(text=locale.change_phone_button)]
    )
    return menu_buttons
