import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config_reader import config
from src.routers.user_actions import user_actions
from src.utils.user_actions import check_user_registration_state

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
dp.include_router(user_actions)
COMPANY_NAME = "Default Company"


@dp.message(CommandStart())
async def start_handler(message: Message):
    menu_buttons = []
    if not check_user_registration_state(message.from_user.id):
        menu_buttons.append(KeyboardButton(text="register"))
    menu_buttons.extend([KeyboardButton(text="change name"), KeyboardButton(text="change phone")])
    await message.answer(
        f"Hello! This bot will help you manage your memberships with {COMPANY_NAME}. Please pick one of the options below:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
