import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.routers.misc import misc
from src.routers.user_actions import user_actions
from src.routers.membership_management import mb_management


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(misc, user_actions, mb_management)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
