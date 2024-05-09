from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config_reader import GlobalSettings
from src.db_calls import admin as db_admin
from src.model.request import RequestType
from src.routers import for_admin
from src.utils import menu, bot_helpers
from src.utils.bot_helpers import IsAdmin
from src.utils.callback_factories import (
    MembershipRequestCallbackFactory,
    MBRequestValueCallbackFactory,
    MBRequestListCallbackFactory,
    FreezeRequestCallbackFactory,
)
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons
from babel.dates import format_date


router = Router()
_ = GlobalSettings().i18n.gettext


@router.callback_query(
    F.data == f"{Action.MANAGE_MEMBERSHIP}{Modifier.CALLBACK}", IsAdmin()
)
async def manage_memberships(callback: CallbackQuery, bot: Bot):
    await callback.message.answer(
        text=_("MANAGE_MEMBERSHIP_options"), reply_markup=menu.mb_management_options()
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(
    F.data == f"{Modifier.ADMIN}{Action.ADD_MEMBERSHIP}{Modifier.CALLBACK}", IsAdmin()
)
async def poll_for_mb_add_request(callback: CallbackQuery, bot: Bot):
    await for_admin.poll_for_requests(
        message=callback.message, request_type=RequestType.ADD_MEMBERSHIP
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(
    F.data == f"{Modifier.ADMIN}{Action.FREEZE_MEMBERSHIP}{Modifier.CALLBACK}",
    IsAdmin(),
)
async def poll_for_mb_freeze_request(callback: CallbackQuery, bot: Bot):
    await for_admin.poll_for_requests(
        message=callback.message, request_type=RequestType.FREEZE_MEMBERSHIP
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(MBRequestListCallbackFactory.filter(), IsAdmin())
async def add_membership_select_member(
    callback: CallbackQuery, callback_data: MBRequestListCallbackFactory, bot: Bot
):
    request = callback_data
    if not request:
        await callback.message.answer(text=_("ADD_MEMBERSHIP_error_expired"))
        await callback.answer()
        return
    membership_values = menu.membership_value_buttons(
        member_tg_id=request.member_tg_id,
        member_name=request.member_name,
        chat_id=request.chat_id,
        request_id=request.id,
    )
    await callback.message.answer(
        text=_("ADD_MEMBERSHIP_query_value"), reply_markup=membership_values
    )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(MBRequestValueCallbackFactory.filter(), IsAdmin())
async def process_membership(
    callback: CallbackQuery, bot: Bot, callback_data: MembershipRequestCallbackFactory
):
    request = callback_data
    if request is None or request.value == 0:
        await callback.message.answer(text=_("ADD_MEMBERSHIP_error_expired"))
        await callback.answer()
        return
    elif request.value == -1:
        await bot.send_message(
            chat_id=request.chat_id,
            text=_("ADD_MEMBERSHIP_declined"),
            reply_markup=main_buttons(user_id=callback.from_user.id),
        )
    else:
        db_admin.add_membership(
            tg_id=request.member_tg_id,
            membership_value=request.value,
            request_id=request.id,
        )
        await callback.message.answer(
            text=_("ADD_MEMBERSHIP_ok_admin").format(
                mb_value=request.value, member_name=request.member_name
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=request.chat_id,
            text=_("ADD_MEMBERSHIP_ok_member").format(mb_value=request.value),
        )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(FreezeRequestCallbackFactory.filter(), IsAdmin())
async def freeze_membership(
    callback: CallbackQuery,
    callback_data: FreezeRequestCallbackFactory,
    bot: Bot,
    state: FSMContext,
):
    request = callback_data
    unfreeze_date = db_admin.freeze_membership(
        mb_id=request.membership_id, days=request.duration, request_id=request.id
    )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    data = await state.get_data()
    await callback.message.answer(
        _("FREEZE_MEMBERSHIP_ok_admin").format(
            unfreeze_date=format_date(date=unfreeze_date, locale=data.get("locale"))
        )
    )
    await bot.send_message(
        chat_id=request.chat_id,
        text=_("FREEZE_MEMBERSHIP_ok_member").format(
            unfreeze_date=format_date(date=unfreeze_date, locale=data.get("locale"))
        ),
    )
    await callback.answer()
