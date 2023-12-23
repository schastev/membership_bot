import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config_reader import config
from src.routers.user_actions import user_actions
from src.routers import membership_management
from src.utils.user_actions import check_user_registration_state, check_admin

logging.basicConfig(level=logging.INFO)
locale = config

dp = Dispatcher()


@dp.message(CommandStart())
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


async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp.include_routers(user_actions, membership_management.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
