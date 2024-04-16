from aiogram.types import Message

from config_reader import config
from src.db_calls import for_admin
from src.model.request import RequestType
from src.utils import translation, menu

_ = translation.i18n.gettext


async def poll_for_requests(message: Message, request_type: RequestType):
    if request_type == RequestType.ADD_MEMBERSHIP:
        request_type_string = _("membership")
        button_name = _("ADD_MEMBERSHIP_button")
        pending_message = _("pending_membership")
        menu_function = menu.membership_request_buttons
    elif request_type == RequestType.ATTENDANCE:
        request_type_string = _("attendance")
        button_name = _("CHECK_IN_button")
        pending_message = _("pending_attendance")
        menu_function = menu.attendance_request_buttons
    elif request_type == RequestType.FREEZE_MEMBERSHIP:
        request_type_string = _("freeze")
        button_name = _("FREEZE_MEMBERSHIP_button")
        pending_message = _("pending_freeze")
        menu_function = menu.freeze_membership_request_buttons
    else:
        request_type_string = _("unfreeze")
        button_name = _("UNFREEZE_MEMBERSHIP_button")
        pending_message = _('pending_unfreeze')
        menu_function = menu.freeze_membership_request_buttons  #todo
    await message.answer(_("polling").format(request_type_string=request_type_string, timeout_seconds=config.polling_timeout_seconds, button_name=button_name))
    requests = await for_admin.poll_for_requests(request_type=request_type)
    if len(requests) == 0:
        await message.answer(_("polling_timeout").format(button_name=button_name))
    else:
        request_buttons = menu_function(request_list=requests)
        await message.answer(text=_("pending_list").format(pending_message), reply_markup=request_buttons)
