from aiogram import Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config_reader import config
from src.utils import menu, db_mb_for_admin, bot_helpers, translation
from src.utils.callback_factories import MembershipRequestCallbackFactory, MBRequestValueCallbackFactory, \
    MBRequestListCallbackFactory
from src.utils.db_user import check_admin
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_manage")
async def manage_memberships(callback: CallbackQuery):
    if not check_admin(callback.from_user.id):
        await callback.message.answer(_("not_admin"))
        await callback.answer()
        return
    await callback.message.answer(_('polling').format(config.polling_timeout_seconds))
    requests = await db_mb_for_admin.poll_for_membership_requests()
    if len(requests) == 0:
        await callback.message.answer(_('polling_timeout'))
    else:
        request_buttons = menu.membership_request_buttons(request_list=requests)
        await callback.message.answer(text=_("pending_requests"), reply_markup=request_buttons)
    await callback.answer()


@router.callback_query(MBRequestListCallbackFactory.filter())
async def add_membership_select_member(callback: CallbackQuery, callback_data: MBRequestListCallbackFactory, bot: Bot):
    request = callback_data
    if not request:
        await callback.message.answer(text=_("request_expired"))
        await callback.answer()
        return
    membership_values = menu.membership_value_buttons(
        member_tg_id=request.member_tg_id,
        member_name=request.member_name,
        chat_id=request.chat_id,
        request_id=request.id
    )
    await callback.message.answer(text=_("select_value"), reply_markup=membership_values)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(MBRequestValueCallbackFactory.filter())
async def process_membership(callback: CallbackQuery, bot: Bot, callback_data: MembershipRequestCallbackFactory):
    request = callback_data
    if request is None or request.value == 0:
        await callback.message.answer(text=_("request_expired"))
        await callback.answer()
        return
    elif request.value == -1:
        await bot.send_message(
            chat_id=request.chat_id,
            text=_("membership_not_added_member"),
            reply_markup=main_buttons(user_id=callback.from_user.id)
        )
    else:
        membership = db_mb_for_admin.add_membership(tg_id=request.member_tg_id, membership_value=request.value)
        await callback.message.answer(
            text=_("membership_added_admin").format(membership.total_amount, request.member_name),
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=request.chat_id, text=_("membership_added_member").format(membership.total_amount)
        )
    db_mb_for_admin.delete_membership_request(request_id=request.id)
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()
