import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config_reader import GlobalSettings
from src.utils.constants import Action, Modifier
from src.utils.menu import UserState

router = Router()


@router.callback_query(F.data.in_(GlobalSettings().config.locales))
async def locale_handler(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    user_state: UserState | None = None,
):
    await GlobalSettings().locale.set_locale(state=state, locale=callback.data)
    if user_id := callback.message.from_user.id == bot.id:
        # this is to correctly display buttons after user changes locale
        user_id = callback.from_user.id
    from src.routers import helpers

    await helpers.greeting(
        message=callback.message, user_id=user_id, user_state=user_state
    )
    from src.db_calls.user import check_user_registration_state

    member = check_user_registration_state(tg_id=user_id)
    if member:
        from src.db_calls.user import update_user_locale

        update_user_locale(tg_id=user_id, new_locale=callback.data)
    from src.utils import bot_helpers

    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    from src.db_calls.user import check_user_registration_state

    if member := check_user_registration_state(message.from_user.id):
        await GlobalSettings().locale.set_locale(state=state, locale=member.locale)
        from src.routers import helpers

        await helpers.greeting(message=message, user_id=member.tg_id)
    else:
        _ = GlobalSettings().i18n.gettext
        greetings = [
            _("first_greeting", locale=loc) for loc in GlobalSettings().config.locales
        ]
        from src.utils.menu import locale_buttons

        await message.answer("\n".join(greetings), reply_markup=locale_buttons())


@router.callback_query(F.data == f"{Action.CANCEL}{Modifier.CALLBACK}")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    _ = GlobalSettings().i18n.gettext
    logging.info(_("cancelled_state_log").format(current_state=current_state))
    from src.utils.menu import main_buttons

    await callback.message.answer(
        _("cancelled"), reply_markup=main_buttons(user_id=callback.from_user.id)
    )
    await state.set_state(None)
    await callback.answer()


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)


@router.callback_query(F.data)
async def gotta_catch_all_of_them(callback: CallbackQuery):
    print(callback.data)
