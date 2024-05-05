from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import config_reader
from src.db_calls import member as db_member
from src.model.request import RequestType
from src.routers import for_member
from src.routers.helpers import get_active_membership_or_go_home
from src.utils import translation, bot_helpers
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons, cancel_button

router = Router()
_ = translation.i18n.gettext


class FreezeRequestState(StatesGroup):
    GET_DURATION = State()


@router.callback_query(F.data == f"{Action.VIEW_ACTIVE_MEMBERSHIP}{Modifier.CALLBACK}")
async def view_active_membership(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if active_membership := await get_active_membership_or_go_home(callback=callback):
        data = await state.get_data()
        await callback.message.answer(
            active_membership.print(locale=data.get("locale")),
            reply_markup=main_buttons(user_id=callback.from_user.id),
        )
        await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(F.data == f"{Action.VIEW_ALL_MEMBERSHIPS}{Modifier.CALLBACK}")
async def view_memberships(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if memberships := db_member.get_memberships_by_user_id(tg_id=callback.from_user.id):
        data = await state.get_data()
        text = "\n".join(mb.past_info(locale=data.get("locale")) for mb in memberships)
    else:
        text = _("VIEW_ALL_MEMBERSHIPS_error_no")
    await callback.message.answer(
        text, reply_markup=main_buttons(user_id=callback.from_user.id)
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(F.data == f"{Action.ADD_MEMBERSHIP}{Modifier.CALLBACK}")
async def request_to_add_membership(callback: CallbackQuery, bot: Bot):
    await for_member.add_request(
        message=callback.message,
        tg_id=callback.from_user.id,
        request_type=RequestType.ADD_MEMBERSHIP,
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(F.data == f"{Action.FREEZE_MEMBERSHIP}{Modifier.CALLBACK}")
async def request_to_freeze_membership(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    await callback.message.answer(
        text=_("FREEZE_MEMBERSHIP_query_duration").format(
            max_freeze_duration=config_reader.config.max_freeze_duration
        ),
        reply_markup=cancel_button(),
    )
    await state.set_state(FreezeRequestState.GET_DURATION)
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.message(FreezeRequestState.GET_DURATION)
async def process_freeze_request(message: Message, state: FSMContext):
    duration = message.text
    try:
        duration = int(duration)
    except ValueError:
        await message.answer(
            text=_("FREEZE_MEMBERSHIP_query_duration").format(
                config_reader.config.max_freeze_duration
            ),
            reply_markup=cancel_button(),
        )
        return
    await for_member.add_request(
        message=message,
        tg_id=message.from_user.id,
        request_type=RequestType.FREEZE_MEMBERSHIP,
        duration=duration,
    )
    await state.set_state(None)


@router.callback_query(F.data == f"{Action.UNFREEZE_MEMBERSHIP}{Modifier.CALLBACK}")
async def unfreeze_membership(callback: CallbackQuery, bot: Bot):
    if active_mb := await get_active_membership_or_go_home(
        tg_id=callback.from_user.id, callback=callback
    ):
        db_member.unfreeze_membership(mb_id=active_mb.id)
        await callback.message.answer(
            text=_("UNFREEZE_MEMBERSHIP_ok"),
            reply_markup=main_buttons(user_id=callback.from_user.id),
        )
        await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
