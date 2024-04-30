import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config_reader import config
from src.db_calls.user import check_user_registration_state, update_user_locale
from src.routers import user, mb_for_admin, mb_for_member, att_for_member, att_for_admin
from src.routers.helpers import greeting
from src.utils import translation, bot_helpers
from src.utils.translation import locale
from src.utils.menu import main_buttons, UserState, locale_buttons


router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data.in_(config.locales))
async def locale_handler(callback: CallbackQuery, state: FSMContext, bot: Bot, user_state: UserState | None = None):
    await translation.locale.set_locale(state=state, locale=callback.data)
    if user_id := callback.message.from_user.id == bot.id:
        # this is to correctly display buttons after user changes locale
        user_id = callback.from_user.id
    await greeting(message=callback.message, user_id=user_id, user_state=user_state)
    member = check_user_registration_state(tg_id=user_id)
    if member:
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


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    locale.setup(dp)
    dp.include_routers(
        user.router, mb_for_admin.router, mb_for_member.router, att_for_member.router, att_for_admin.router, router
    )
    bot = Bot(token=config.bot_token.get_secret_value())
    await dp.start_polling(bot)


def main_menu(user_id: int, user_state: UserState):
    # this is a proxy functions, since it makes no sense to me to bring here a functino that assembles menu buttons.
    # the rest of the functions are somewhat justifiable, since they are at least directly dispatcher/bot related
    # more so then the keyboard buttons anyway
    return main_buttons(user_id=user_id, user_state=user_state)


if __name__ == "__main__":
    asyncio.run(main())
