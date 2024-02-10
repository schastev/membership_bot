from aiogram import Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
#
from config_reader import config
from src.utils import menu, bot_helpers, translation
from src.db_calls import att_for_admin, mb_for_member
from src.utils.callback_factories import AttRequestCallbackFactory
from src.db_calls.user import is_admin

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_manage_att")
async def manage_attendances(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.message.answer(_("not_admin"))
        await callback.answer()
        return
    await callback.message.answer(_('polling_att').format(config.polling_timeout_seconds))
    requests = await att_for_admin.poll_for_attendance_requests()
    if len(requests) == 0:
        await callback.message.answer(_('polling_timeout_att'))
    else:
        request_buttons = menu.attendance_request_buttons(request_list=requests)
        await callback.message.answer(text=_("pending_requests_att"), reply_markup=request_buttons)
    await callback.answer()


@router.callback_query(AttRequestCallbackFactory.filter())
async def mark_attendance(callback: CallbackQuery, callback_data: AttRequestCallbackFactory, bot: Bot):
    request = callback_data
    if not request:
        await callback.message.answer(text=_("request_expired"))
        await callback.answer()
        return
    membership = mb_for_member.view_memberships_by_user_id(tg_id=request.member_tg_id)[0]
    # todo add a catch for failed subtract
    attendance = att_for_admin.mark_attendance(tg_id=request.member_tg_id, membership_id=membership.id)
    await callback.message.answer(
        text=_("attendance_marked_admin"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=request.chat_id, text=_("attendance_marked_member")
    )
    att_for_admin.delete_attendance_request(request_id=request.id)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()
