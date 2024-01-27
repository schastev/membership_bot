from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import translation
from config_reader import config
from src.utils.db_user import check_user_registration_state
from src.utils.menu import main_buttons, language_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data.in_(config.languages))
async def handle_language(callback: CallbackQuery, state: FSMContext):
    await translation.locale.set_locale(state=state, locale=callback.data)
    await state.update_data(lang=callback.data)
    await greeting(message=callback.message)
    await callback.answer()


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if not check_user_registration_state(message.from_user.id) and not lang:
        menu_buttons = language_buttons()
        greetings = [_("first_greeting", locale=language) for language in config.languages]
        await message.answer("\n".join(greetings), reply_markup=menu_buttons)
    else:
        await greeting(message=message)


async def greeting(message: Message):
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        _("greeting").format(config.company_name), reply_markup=menu_buttons
    )


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)


@router.callback_query(F.data)
async def gotta_catch_all_of_them(callback: CallbackQuery):
    print(callback.data)
