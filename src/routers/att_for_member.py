from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.model.request import RequestType
from src.routers import for_member
from src.utils import translation
from src.db_calls import att_for_member, att_for_admin, mb_for_member, for_admin
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_view_att")
async def view_attendances(callback: CallbackQuery):
    attendance_list = att_for_member.view_attendances_for_active_membership(tg_id=callback.from_user.id)
    if len(attendance_list) == 0:
        text = _("no_attendances")
    else:
        text = "\n".join([str(att) for att in attendance_list])
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_add_att")
async def request_to_add_attendance(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_membership:
        await callback.message.answer(text=_("membership_expired_or_used_up"))
    else:
        await for_member.add_request(
            message=callback.message,
            member_id=callback.from_user.id,
            request_type=RequestType.ATTENDANCE,
            active_membership_id=active_membership.id,
        )
    await callback.answer()
