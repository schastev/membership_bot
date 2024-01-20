import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.routers import misc, user, mb_for_admin, mb_for_member
from translation import t


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(user.router, mb_for_admin.router, mb_for_member.router, misc.router)
    bot = Bot(token=config.bot_token.get_secret_value())
    t.install()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
