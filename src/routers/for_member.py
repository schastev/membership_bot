from aiogram.types import Message

from src.db_calls import for_admin, mb_for_member, att_for_member
from src.model.request import RequestType
from src.utils import translation
from src.utils import menu


_ = translation.i18n.gettext


async def add_request(
        message: Message, member_id: int, request_type: RequestType, duration: int = 0, active_membership_id: int = 0
) -> bool:
    if request_type == RequestType.ADD_MEMBERSHIP:
        add_function = mb_for_member.request_to_add_membership
        args = {"tg_id": member_id, "chat_id": message.chat.id}
        sent_message = _("request_sent_mb")
    elif request_type == RequestType.ATTENDANCE:
        if not active_membership_id:
            raise ValueError
        add_function = att_for_member.request_to_add_attendance
        args = {"tg_id": member_id, "chat_id": message.chat.id, "mb_id": active_membership_id}
        sent_message = _("request_sent_att")
    elif request_type == RequestType.FREEZE_MEMBERSHIP:
        add_function = mb_for_member.request_to_freeze_membership
        if not duration or not active_membership_id:
            raise ValueError
        args = {"tg_id": member_id, "chat_id": message.chat.id, "mb_id": active_membership_id, "duration": duration}
        sent_message = _("request_sent_freeze")
    else:  # todo
        add_function = mb_for_member.request_to_freeze_membership
        if not duration or not active_membership_id:
            raise ValueError
        args = {"tg_id": member_id, "chat_id": message.chat.id, "mb_id": active_membership_id}
        sent_message = _("request_sent_unfreeze")
        pass

    existing_requests = for_admin.check_existing_requests(tg_id=member_id, request_type=request_type)
    if len(existing_requests) == 0:
        add_function(**args)
        text = sent_message
        request_added = True
    else:
        text = _("request_already_existed")
        request_added = False
    await message.answer(text=text, reply_markup=menu.main_buttons(user_id=member_id))
    # todo rm buttons
    return request_added