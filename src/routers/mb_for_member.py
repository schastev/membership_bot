from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import config_reader
from src.model.request import RequestType
from src.routers import for_member
from src.utils import translation
from src.db_calls import mb_for_member, for_admin
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


class FreezeRequestState(StatesGroup):
    GET_DURATION = State()


@router.callback_query(F.data == f"{Action.VIEW_ACTIVE_MEMBERSHIP}{Modifier.CALLBACK}")
async def view_active_membership(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_membership:
        text = _("VIEW_ACTIVE_MEMBERSHIP_error_no")
    else:
        text = str(active_membership)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == f"{Action.VIEW_ALL_MEMBERSHIPS}{Modifier.CALLBACK}")
async def view_memberships(callback: CallbackQuery):
    memberships = mb_for_member.get_memberships_by_user_id(tg_id=callback.from_user.id)
    if not memberships:
        text = _("VIEW_ALL_MEMBERSHIPS_error_no")
    else:
        text = str(memberships)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == f"{Action.ADD_MEMBERSHIP}{Modifier.CALLBACK}")
async def request_to_add_membership(callback: CallbackQuery):
    await for_member.add_request(
        message=callback.message, member_id=callback.from_user.id, request_type=RequestType.ADD_MEMBERSHIP
    )
    await callback.answer()


@router.callback_query(F.data == f"{Action.FREEZE_MEMBERSHIP}{Modifier.CALLBACK}")
async def request_to_freeze_membership(callback: CallbackQuery, state: FSMContext):
    active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_mb.activation_date:
        await callback.message.answer(text=_("FREEZE_MEMBERSHIP_error_not_active"))
    else:
        existing_requests = for_admin.check_existing_requests(
            tg_id=callback.from_user.id, request_type=RequestType.FREEZE_MEMBERSHIP
        )
        if not existing_requests:
            await callback.message.answer(text=_("FREEZE_MEMBERSHIP_query_duration").format(config_reader.config.max_freeze_duration))
            await state.set_state(FreezeRequestState.GET_DURATION)
    await callback.answer()


@router.message(FreezeRequestState.GET_DURATION)
async def process_freeze_request(message: Message, state: FSMContext):
    duration = message.text
    try:
        duration = int(duration)
    except ValueError:
        await message.answer(text=_("FREEZE_MEMBERSHIP_query_duration").format(config_reader.config.max_freeze_duration))
        return
    active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=message.from_user.id)
    try:
        active_mb.is_valid_freeze_date(days=duration)
    except ValueError as error:
        await message.answer(text=error.args[0])
        await state.set_state(None)
        return
    mb_for_member.request_to_freeze_membership(
        tg_id=message.from_user.id, chat_id=message.chat.id, mb_id=active_mb.id, duration=duration
    )
    await message.answer(text=_("REQUEST_sent").format(request_type=RequestType.FREEZE_MEMBERSHIP))
    await state.set_state(None)

