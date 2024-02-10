from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import translation
from config_reader import config
from src.utils import bot_helpers
from src.utils.db_user import check_user_registration_state, update_user_locale
from src.utils.menu import main_buttons, language_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data.in_(config.languages))
async def handle_language(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await translation.locale.set_locale(state=state, locale=callback.data)
    if callback.message.from_user.id == bot.id:  # this is to correctly display buttons after user changes locale
        user_id = callback.from_user.id
    else:
        user_id = callback.message.from_user.id
    await greeting(message=callback.message, user_id=user_id)
    user = check_user_registration_state(tg_id=user_id)
    if user:
        update_user_locale(tg_id=user_id, new_locale=callback.data)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    user = check_user_registration_state(message.from_user.id)
    if not user:
        menu_buttons = language_buttons()
        greetings = [_("first_greeting", locale=language) for language in config.languages]
        await message.answer("\n".join(greetings), reply_markup=menu_buttons)
    else:
        await translation.locale.set_locale(state=state, locale=user.locale)
        await greeting(message=message)


async def greeting(message: Message, user_id: int = 0):
    menu_buttons = main_buttons(user_id=user_id or message.from_user.id)
    await message.answer(
        _("greeting").format(config.company_name), reply_markup=menu_buttons
    )


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)


@router.callback_query(F.data)
async def gotta_catch_all_of_them(callback: CallbackQuery):
    print(callback.data)
