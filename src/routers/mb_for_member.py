from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import config_reader
import src.db_calls.for_admin
from src.model.request import RequestType
from src.routers import for_member
from src.utils import translation
from src.db_calls import mb_for_member, mb_for_admin, for_admin
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


class FreezeRequestState(StatesGroup):
    GET_DURATION = State()


@router.callback_query(F.data == "button_view_active_mb")
async def view_active_membership(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_membership:
        text = _("no_active_memberships")
    else:
        text = str(active_membership)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_view_mb")
async def view_memberships(callback: CallbackQuery):
    memberships = mb_for_member.get_memberships_by_user_id(tg_id=callback.from_user.id)
    if not memberships:
        text = _("no_memberships")
    else:
        text = str(memberships)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_add_mb")
async def request_to_add_membership(callback: CallbackQuery):
    await for_member.add_request(
        message=callback.message, member_id=callback.from_user.id, request_type=RequestType.ADD_MEMBERSHIP
    )
    await callback.answer()


@router.callback_query(F.data == "button_freeze_mb")
async def request_to_freeze_membership(callback: CallbackQuery, state: FSMContext):
    active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_mb.activation_date:
        await callback.message.answer(text=_("mb_not_activated_yet"))
    else:
        existing_requests = for_admin.check_existing_requests(
            tg_id=callback.from_user.id, request_type=RequestType.FREEZE_MEMBERSHIP
        )
        if not existing_requests:
            await callback.message.answer(text=_("freeze_duration_query".format(config_reader.config.max_freeze_duration)))
            await state.set_state(FreezeRequestState.GET_DURATION)
    await callback.answer()


@router.message(FreezeRequestState.GET_DURATION)
async def process_freeze_request(message: Message, state: FSMContext):
    duration = message.text
    try:
        duration = int(duration)
        is_number = True
    except ValueError:
        is_number = False
    is_valid_length = False
    if is_number:
        is_valid_length = duration <= config_reader.config.max_freeze_duration
    if not is_number or not is_valid_length:
        await message.answer(_("invalid_duration").format(config_reader.config.max_freeze_duration))
        return
    active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=message.from_user.id)
    mb_for_member.request_to_freeze_membership(
        tg_id=message.from_user.id, chat_id=message.chat.id, mb_id=active_mb.id, duration=duration
    )
    await message.answer(text=_("request_sent_freeze"))
    await state.set_state(None)

