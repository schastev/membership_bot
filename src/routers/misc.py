from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup

from config_reader import config
from src.utils.db_user import check_user_registration_state
import translation
from src.utils.menu import main_buttons, language_buttons


router = Router()
__ = translation.i18n.lazy_gettext


@router.message(F.text.in_(config.languages))
async def handle_language(message: Message, state: FSMContext):
    await state.update_data(locale=message.text)
    await translation.locale.set_locale(state=state, locale=message.text)
    await state.update_data(lang=message.text)
    await greeting(message=message)


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if not check_user_registration_state(message.from_user.id) and not lang:
        menu_buttons = language_buttons()
        await message.answer("Hello! Please select your language from the list below.\n"
                             "Здравствуйте! Выберите язык из списка ниже.",
                             reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
                             )
    else:
        await greeting(message=message)


async def greeting(message: Message):
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        __("greeting").format(config.company_name),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)
