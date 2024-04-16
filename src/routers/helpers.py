from typing import Union

from aiogram.types import CallbackQuery, Message

from src.db_calls import mb_for_member
from src.model.membership import Membership
from src.utils import translation
from src.utils.menu import main_buttons

_ = translation.i18n.gettext


async def get_active_membership_or_go_home(
    tg_id: Union[int, None] = None,
    callback: Union[CallbackQuery, None] = None,
    message: Union[Message, None] = None,
    error_message: Union[str, None] = None
) -> Union[Membership, None]:
    if callback:
        answer = callback.message
        user_id = tg_id or callback.from_user.id
    elif message:
        answer = message
        user_id = tg_id or message.from_user.id
    else:
        raise ValueError("There should be either a message or a callback!")
    if not error_message:
        error_message = _("VIEW_ACTIVE_MEMBERSHIP_error_no")
    active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=user_id)
    if not active_mb:
        await answer.answer(error_message, reply_markup=main_buttons(user_id=user_id))
        if callback:
            await callback.answer()
    else:
        return active_mb
