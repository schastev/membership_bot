from aiogram.types import Message

from config_reader import config
from src.db_calls import for_admin
from src.db_calls.user import is_admin
from src.model.request import RequestType
from src.utils import translation, menu

_ = translation.i18n.gettext


async def poll_for_requests(message: Message, request_type: RequestType):
    if request_type == RequestType.ADD_MEMBERSHIP:
        polling_message = _('polling_mb')
        timeout_message = _('polling_timeout_mb')
        pending_message = _("pending_requests_mb")
        menu_function = menu.membership_request_buttons
    elif request_type == RequestType.ATTENDANCE:
        polling_message = _('polling_att')
        timeout_message = _('polling_timeout_att')
        pending_message = _("pending_requests_att")
        menu_function = menu.attendance_request_buttons
    elif request_type == RequestType.FREEZE_MEMBERSHIP:
        polling_message = _('polling_freeze')
        timeout_message = _('polling_timeout_freeze')
        pending_message = _("pending_requests_freeze")
        menu_function = menu.freeze_membership_request_buttons
    else:
        polling_message = _('polling_unfreeze')
        timeout_message = _('polling_timeout_unfreeze')
        pending_message = _("pending_requests_unfreeze")
        menu_function = menu.freeze_membership_request_buttons  #todo
    await message.answer(polling_message.format(config.polling_timeout_seconds))
    requests = await for_admin.poll_for_requests(request_type=request_type)
    if len(requests) == 0:
        await message.answer(timeout_message)
    else:
        request_buttons = menu_function(request_list=requests)
        await message.answer(text=pending_message, reply_markup=request_buttons)


async def check_admin(user_id: int, message: Message) -> bool:
    if not is_admin(user_id):
        await message.answer(_("not_admin"))
        return False
    return True
