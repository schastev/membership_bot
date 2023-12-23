from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup

from config_reader import config
from src.utils.menu_utils import compile_menu

router = Router()
locale = config


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message):
    menu_buttons = compile_menu(message)
    await message.answer(
        locale.greeting.format(locale.company_name),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)
