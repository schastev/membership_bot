from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from config_reader import config
from src.utils.user_actions import check_admin, check_user_registration_state

misc = Router()
locale = config


@misc.message(CommandStart())
@misc.message(F.text.casefold() == "start")
async def start_handler(message: Message):
    menu_buttons = []
    if check_admin(message.from_user.id):
        menu_buttons.append(KeyboardButton(text=locale.manage_button))
    elif not check_user_registration_state(message.from_user.id):
        menu_buttons.append(KeyboardButton(text=locale.register_button))
    menu_buttons.extend(
        [KeyboardButton(text=locale.change_name_button), KeyboardButton(text=locale.change_phone_button)]
    )
    await message.answer(
        locale.greeting.format(locale.company_name),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )
