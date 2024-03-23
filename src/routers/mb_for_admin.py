from aiogram import Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from src.model.request import RequestType
from src.routers import for_admin
from src.utils import menu, bot_helpers, translation
from src.db_calls import mb_for_admin
from src.utils.bot_helpers import IsAdmin
from src.utils.callback_factories import MembershipRequestCallbackFactory, MBRequestValueCallbackFactory, \
    MBRequestListCallbackFactory, FreezeRequestCallbackFactory
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_manage", IsAdmin())
async def manage_memberships(callback: CallbackQuery):
    management_options = menu.mb_management_options()
    await callback.message.answer(text=_("management_options"), reply_markup=management_options)
    await callback.answer()


@router.callback_query(F.data == "button_add_mb_request", IsAdmin())
async def poll_for_mb_add_request(callback: CallbackQuery):
    await for_admin.poll_for_requests(message=callback.message, request_type=RequestType.ADD_MEMBERSHIP)
    await callback.answer()


@router.callback_query(F.data == "button_freeze_mb_request", IsAdmin())
async def poll_for_mb_freeze_request(callback: CallbackQuery):
    await for_admin.poll_for_requests(message=callback.message, request_type=RequestType.FREEZE_MEMBERSHIP)
    await callback.answer()


@router.callback_query(MBRequestListCallbackFactory.filter(), IsAdmin())
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


@router.callback_query(MBRequestValueCallbackFactory.filter(), IsAdmin())
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
        mb_for_admin.add_membership(tg_id=request.member_tg_id, membership_value=request.value, request_id=request.id)
        await callback.message.answer(
            text=_("membership_added_admin").format(request.value, request.member_name),
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=request.chat_id, text=_("membership_added_member").format(request.value)
        )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(FreezeRequestCallbackFactory.filter(), IsAdmin())
async def freeze_membership(callback: CallbackQuery, callback_data: FreezeRequestCallbackFactory, bot: Bot):
    request = callback_data
    mb_for_admin.freeze_membership(mb_id=request.membership_id, days=request.duration, request_id=request.id)
    await callback.message.answer(_("mb_frozen_admin"))
    await bot.send_message(chat_id=request.chat_id, text=_("mb_frozen_member"))
    await callback.answer()
