from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

import translation
from config_reader import config
from src.utils import menu, db_mb_for_admin
from src.utils.db_user import check_admin
from src.utils.menu import main_buttons

router = Router()
locale = config
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_manage")
async def manage_memberships(callback: CallbackQuery, state: FSMContext):
    if not check_admin(callback.from_user.id):
        await callback.message.answer(_("not_admin"))
        await callback.answer()
        return
    await callback.message.answer(_('polling').format(config.polling_timeout_seconds))
    requests = await db_mb_for_admin.poll_for_membership_requests()
    if len(requests) == 0:
        await callback.message.answer(_('polling_timeout'))
        await callback.answer()
    else:
        await state.update_data(requests=requests)
        request_buttons = menu.membership_request_buttons(request_list=requests)
        await callback.message.answer(
            text=_("pending_requests"), reply_markup=request_buttons, resize_keyboard=False
        )
        await callback.answer()


@router.callback_query(F.data.startswith("mp_request_"))
async def add_membership_select_member(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    requests = data.get("requests")
    await state.update_data(requests=None)
    member_tg_id = callback.data.split("_")[-1]
    if requests is None:
        await callback.message.answer(
            text=_("request_expired"),
            reply_markup=ReplyKeyboardRemove(),
        )
        await callback.answer()
        return
    request = [r for r in requests if r.get("member").tg_id == int(member_tg_id)][0]
    await state.update_data(request=request)
    membership_values = menu.membership_value_buttons()
    await callback.message.answer(
        text=_("select_value"), reply_markup=membership_values, resize_keyboard=False
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mb_value_"))
async def process_membership(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    request = data.get("request")
    await state.update_data(request=None)
    mb_value = callback.data.split("_")[-1]
    if request is None:
        await callback.message.answer(
            text=_("request_expired"),
            reply_markup=ReplyKeyboardRemove(),
        )
        await callback.answer()
        return
    elif mb_value.casefold() == "decline" and request is not None:
        await bot.send_message(
            chat_id=request["request"].chat_id,
            text=_("membership_not_added_member"),
            reply_markup=main_buttons(user_id=callback.from_user.id)
        )
    else:
        value = int(mb_value)
        member_tg_id = request["request"].tg_id
        member_name = request["member"].name
        membership = db_mb_for_admin.add_membership(tg_id=member_tg_id, membership_value=value)
        await callback.message.answer(
            text=_("membership_added_admin").format(membership.total_amount, member_name),
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=request["request"].chat_id,
            text=_("membership_added_member").format(membership.total_amount)
        )
    db_mb_for_admin.delete_membership_request(request=request["request"])
    await callback.answer()
