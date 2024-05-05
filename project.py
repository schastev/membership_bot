import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config_reader import config
from src.db_calls.user import check_user_registration_state, update_user_locale
from src.routers import (
    user,
    misc,
    mb_for_admin,
    mb_for_member,
    att_for_member,
    att_for_admin,
    helpers,
)
from src.utils import translation, bot_helpers
from src.utils.constants import Action, Modifier
from src.utils.translation import locale
from src.utils.menu import main_buttons, UserState, locale_buttons


router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data.in_(config.locales))
async def locale_handler(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    user_state: UserState | None = None,
):
    await translation.locale.set_locale(state=state, locale=callback.data)
    if user_id := callback.message.from_user.id == bot.id:
        # this is to correctly display buttons after user changes locale
        user_id = callback.from_user.id
    await helpers.greeting(
        message=callback.message, user_id=user_id, user_state=user_state
    )
    member = check_user_registration_state(tg_id=user_id)
    if member:
        update_user_locale(tg_id=user_id, new_locale=callback.data)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.message(CommandStart())
@router.message(F.text.casefold() == "start")
async def start_handler(message: Message, state: FSMContext):
    if member := check_user_registration_state(message.from_user.id):
        await translation.locale.set_locale(state=state, locale=member.locale)
        await helpers.greeting(message=message, user_id=member.tg_id)
    else:
        greetings = [_("first_greeting", locale=loc) for loc in config.locales]
        await message.answer("\n".join(greetings), reply_markup=locale_buttons())


@router.callback_query(F.data == f"{Action.CANCEL}{Modifier.CALLBACK}")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(_("cancelled_state_log").format(current_state=current_state))
    await callback.message.answer(
        _("cancelled"), reply_markup=main_buttons(user_id=callback.from_user.id)
    )
    await state.set_state(None)
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    locale.setup(dp)
    dp.include_routers(
        user.router,
        mb_for_admin.router,
        mb_for_member.router,
        att_for_member.router,
        att_for_admin.router,
        router,
        misc.router,
    )
    bot = Bot(token=config.bot_token.get_secret_value())
    await bot_helpers.set_main_menu(bot=bot)
    await dp.start_polling(bot)


def main_menu(user_id: int, user_state: UserState):
    # this is a proxy function, since it makes no sense to me to bring here a function that assembles menu buttons.
    # the rest of the functions are somewhat justifiable, since they are at least directly dispatcher/bot related
    # more so then the keyboard buttons anyway
    return main_buttons(user_id=user_id, user_state=user_state)


if __name__ == "__main__":
    asyncio.run(main())
