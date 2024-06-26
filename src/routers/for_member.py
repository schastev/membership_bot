from aiogram.types import Message

from config_reader import GlobalSettings
from src.db_calls import member as db_member, admin as db_admin
from src.model.request import RequestType
from src.routers.helpers import get_active_membership_or_go_home
from src.utils import menu


_ = GlobalSettings().i18n.gettext


async def add_request(
    message: Message, tg_id: int, request_type: RequestType, duration: int = 0
) -> bool:
    if request_type == RequestType.ADD_MEMBERSHIP:
        add_function = db_member.request_to_add_membership
        args = {"tg_id": tg_id, "chat_id": message.chat.id}
        pending_message = _("pending_membership")
    else:
        active_mb = await get_active_membership_or_go_home(
            tg_id=message.chat.id, message=message
        )
        if request_type == RequestType.ATTENDANCE:
            if not active_mb:
                return False
            add_function = db_member.request_to_add_attendance
            args = {
                "tg_id": tg_id,
                "chat_id": message.chat.id,
                "mb_id": active_mb.id,
            }
            pending_message = _("pending_attendance")
        elif request_type == RequestType.FREEZE_MEMBERSHIP:
            add_function = db_member.request_to_freeze_membership
            try:
                active_mb.is_valid_freeze_date(days=duration)
            except ValueError as error:
                await message.answer(text=error.args[0])
                return False
            if not duration or not active_mb:
                return False
            args = {
                "tg_id": tg_id,
                "chat_id": message.chat.id,
                "mb_id": active_mb.id,
                "duration": duration,
            }
            pending_message = _("pending_freeze")
        else:
            raise ValueError("Unsupported request type")
    existing_requests = db_admin.check_existing_requests(
        tg_id=tg_id, request_type=request_type
    )
    if existing_requests and existing_requests[0].duration == -1:
        db_admin.delete_request(existing_requests[0].id)
        existing_requests = []
    if len(existing_requests) == 0:
        add_function(**args)
        text = _("REQUEST_sent").format(request_type=pending_message)
        request_added = True
    else:
        text = _("REQUEST_error_already_existed")
        request_added = False
    await message.answer(text=text, reply_markup=menu.main_buttons(user_id=tg_id))
    # todo rm buttons
    return request_added
