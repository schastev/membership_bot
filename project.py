import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.routers import misc, user, mb_for_admin, mb_for_member, att_for_member, att_for_admin
from src.utils.translation import locale
from src.utils.menu import main_buttons, UserState


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    locale.setup(dp)
    dp.include_routers(
        user.router, mb_for_admin.router, mb_for_member.router, att_for_member.router, att_for_admin.router, misc.router
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
