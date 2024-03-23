from aiogram import Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from src.model.attendance import Attendance
from src.model.request import RequestType
from src.routers import for_admin
from src.utils import bot_helpers, translation
from src.db_calls import att_for_admin
from src.utils.bot_helpers import IsAdmin
from src.utils.callback_factories import AttRequestCallbackFactory

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_manage_att", IsAdmin())
async def manage_attendances(callback: CallbackQuery):
    await for_admin.poll_for_requests(message=callback.message, request_type=RequestType.ATTENDANCE)
    await callback.answer()


@router.callback_query(AttRequestCallbackFactory.filter(), IsAdmin())
async def mark_attendance(callback: CallbackQuery, callback_data: AttRequestCallbackFactory, bot: Bot):
    request = callback_data
    if not request:
        await callback.message.answer(text=_("request_expired"))
        await callback.answer()
        return
    attendance = Attendance(member_id=request.member_tg_id, membership_id=request.membership_id)
    current_amount = att_for_admin.mark_attendance(attendance=attendance, request_id=request.id)
    await callback.message.answer(
        text=_("attendance_marked_admin"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=request.chat_id, text=_("attendance_marked_member. Left: {}").format(current_amount)
    )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()
