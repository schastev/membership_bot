from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message, BotCommand

from config_reader import GlobalSettings

_ = GlobalSettings().i18n.gettext


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
        return message.from_user.id in GlobalSettings().config.admin_ids
