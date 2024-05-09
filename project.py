import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher

from config_reader import GlobalSettings


async def main():
    GlobalSettings(prod_env=True)
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    GlobalSettings().locale.setup(dp)
    from src.routers import (
        user,
        misc,
        mb_for_admin,
        mb_for_member,
        att_for_member,
        att_for_admin,
    )

    dp.include_routers(
        user.router,
        mb_for_admin.router,
        mb_for_member.router,
        att_for_member.router,
        att_for_admin.router,
        misc.router,
    )
    bot = Bot(token=GlobalSettings().config.bot_token.get_secret_value())
    from src.utils import bot_helpers

    await bot_helpers.set_main_menu(bot=bot)
    await dp.start_polling(bot)


def main_menu(user_id: int, user_state: Any):
    # this is a proxy function, since it makes no sense to me to bring here a function that assembles menu buttons.
    # the rest of the functions are somewhat justifiable, since they are at least directly dispatcher/bot related
    # more so then the keyboard buttons anyway
    from src.utils.menu import main_buttons

    return main_buttons(user_id=user_id, user_state=user_state)


if __name__ == "__main__":
    asyncio.run(main())
