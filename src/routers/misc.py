import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import config_reader
from config_reader import config
from src.routers.user import _
from src.utils import bot_helpers, translation
from src.db_calls.user import check_user_registration_state, update_user_locale
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons, locale_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data.in_(config.locales))
async def handle_locale(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await translation.locale.set_locale(state=state, locale=callback.data)
    if user_id := callback.message.from_user.id == bot.id:
        # this is to correctly display buttons after user changes locale
        user_id = callback.from_user.id
    await greeting(message=callback.message, user_id=user_id)
    user = check_user_registration_state(tg_id=user_id)
    if user:
        update_user_locale(tg_id=user_id, new_locale=callback.data)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    if user := check_user_registration_state(message.from_user.id):
        await translation.locale.set_locale(state=state, locale=user.locale)
        await greeting(message=message, user_id=user.tg_id)
    else:
        greetings = [_("first_greeting", locale=locale) for locale in config.locales]
        await message.answer("\n".join(greetings), reply_markup=locale_buttons())


async def greeting(message: Message, user_id: int):
    await message.answer(
        _("greeting").format(company_name=config.company_name), reply_markup=main_buttons(user_id=user_id)
    )


@router.callback_query(F.data == f"{Action.CANCEL}{Modifier.CALLBACK}")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(_("cancelled_state_log").format(current_state=current_state))
    await callback.message.answer(_("cancelled"), reply_markup=main_buttons(user_id=callback.from_user.id))
    await state.set_state(None)
    await callback.answer()


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)


@router.callback_query(F.data)
async def gotta_catch_all_of_them(callback: CallbackQuery):
    print(callback.data)
