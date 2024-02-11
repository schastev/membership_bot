from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.utils import translation
from src.db_calls import att_for_member, att_for_admin, mb_for_member
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_view_att")
async def view_attendances(callback: CallbackQuery):
    attendance_list = att_for_member.view_attendances_by_user_id(tg_id=callback.from_user.id)
    if len(attendance_list) == 0:
        text = _("no_attendances")
    else:
        attendance = attendance_list[0]
        # todo prep attendances for printing
        text = _("attendance_info").format(attendance)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_add_att")
async def request_to_add_attendance(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if active_membership.is_expired():
        await callback.message.answer(text=_("membership_expired"))
    elif not active_membership.has_uses():
        await callback.message.answer(text=_("membership_used_up"))
        await callback.answer()
        return
    existing_requests = att_for_admin.check_existing_attendance_requests(tg_id=callback.from_user.id)
    if len(existing_requests) == 0:
        att_for_member.request_to_add_attendance(tg_id=callback.from_user.id, chat_id=callback.message.chat.id)
        text = _("request_sent_att")
    else:
        text = _("request_already_existed")
    await callback.message.answer(text=text, reply_markup=main_buttons(user_id=callback.from_user.id))
    # todo rm buttons
    await callback.answer()
