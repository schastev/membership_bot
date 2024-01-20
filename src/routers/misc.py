from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup

from config_reader import config
from translation import t
from src.utils.menu import main_buttons

router = Router()
config = config
_ = t.gettext


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message):
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        _("greeting").format(config.company_name),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)
