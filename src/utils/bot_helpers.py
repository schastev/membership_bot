from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

import config_reader


async def rm_buttons_from_last_message(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config_reader.config.admin_ids
