import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.routers import misc
from src.routers import user_actions
from src.routers import membership_management

BOT = Bot(token=config.bot_token.get_secret_value())


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(user_actions.router, membership_management.router, misc.router)
    await dp.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
