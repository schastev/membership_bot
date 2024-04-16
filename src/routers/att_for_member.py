from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.model.request import RequestType
from src.routers import for_member
from src.utils import translation
from src.db_calls import att_for_member, mb_for_member
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == f"{Action.VIEW_ATTENDANCES}{Modifier.CALLBACK}")
async def view_attendances(callback: CallbackQuery):
    attendance_list = att_for_member.view_attendances_for_active_membership(tg_id=callback.from_user.id)
    if len(attendance_list) == 0:
        text = _("CHECK_IN_none")
    else:
        text = "\n".join([str(att) for att in attendance_list])
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == f"{Action.CHECK_IN}{Modifier.CALLBACK}")
async def request_to_add_attendance(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_membership:
        await callback.message.answer(text=_("CHECK_IN_error_invalid_membership"))
    else:
        await for_member.add_request(
            message=callback.message,
            member_id=callback.from_user.id,
            request_type=RequestType.ATTENDANCE,
            active_membership_id=active_membership.id,
        )
    await callback.answer()
