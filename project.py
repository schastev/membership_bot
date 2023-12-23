import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.routers import misc
from src.routers import user
from src.routers import membership


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(user.router, membership.router, misc.router)
    bot = Bot(token=config.bot_token.get_secret_value())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
