from aiogram import Bot
from aiogram.types import CallbackQuery


async def rm_buttons_from_last_message(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None
    )
