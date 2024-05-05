from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message, BotCommand

import config_reader
from src.utils import translation

_ = translation.i18n.gettext


async def rm_buttons_from_last_message(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )


async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(command="/start", description=_("MENU_desc"))]
    await bot.set_my_commands(main_menu_commands)


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config_reader.config.admin_ids
