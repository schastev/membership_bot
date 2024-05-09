from aiogram import Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config_reader import GlobalSettings
from src.db_calls import admin as db_admin
from src.model.attendance import Attendance
from src.model.request import RequestType
from src.routers import for_admin
from src.utils import bot_helpers
from src.utils.callback_factories import AttRequestCallbackFactory
from src.utils.constants import Action, Modifier

router = Router()
_ = GlobalSettings().i18n.gettext


@router.callback_query(
    F.data == f"{Action.MANAGE_ATTENDANCE}{Modifier.CALLBACK}", bot_helpers.IsAdmin()
)
async def poll_for_check_in_request(callback: CallbackQuery, bot: Bot):
    await for_admin.poll_for_requests(
        message=callback.message, request_type=RequestType.ATTENDANCE
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(AttRequestCallbackFactory.filter(), bot_helpers.IsAdmin())
async def mark_attendance(
    callback: CallbackQuery, callback_data: AttRequestCallbackFactory, bot: Bot
):
    request = callback_data
    if not request:
        await callback.message.answer(text=_("CHECK_IN_error_expired"))
        await callback.answer()
        return
    attendance = Attendance(
        tg_id=request.member_tg_id, membership_id=request.membership_id
    )
    current_amount = db_admin.mark_attendance(
        attendance=attendance, request_id=request.id
    )
    await callback.message.answer(
        text=_("CHECK_in_ok_admin").format(name=request.member_name),
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=request.chat_id,
        text=_("CHECK_in_ok_member").format(current_amount=current_amount),
    )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()
