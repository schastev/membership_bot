from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery

import translation
from config_reader import config
from src.utils import menu, db_mb_for_admin
from src.utils.db_user import check_admin
from src.utils.menu import main_buttons

router = Router()
locale = config
_ = translation.i18n.gettext


class MembershipManagementStates(StatesGroup):
    SELECT_MEMBER = State()
    SELECT_VALUE = State()


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
        request_buttons = menu.membership_request_buttons(requests)
        await callback.message.answer(
            text=_("pending_requests"), reply_markup=request_buttons, resize_keyboard=True
        )
        await callback.answer()
        await state.set_state(MembershipManagementStates.SELECT_MEMBER)


@router.message(MembershipManagementStates.SELECT_MEMBER)
async def add_membership_select_member(message: Message, state: FSMContext):
    data = await state.get_data()
    requests = data.get("requests")
    member_name, member_phone = message.text.split(": ")
    request = [r for r in requests if r["member"].name == member_name and r["member"].phone == float(member_phone)]
    await state.update_data(request_tg_id=request[0]["request"].tg_id)
    await state.update_data(request=request[0])
    membership_values = menu.membership_value_buttons()
    await message.answer(
        text=_("select_value"),
        reply_markup=ReplyKeyboardMarkup(keyboard=[membership_values], resize_keyboard=True)
    )
    await state.set_state(MembershipManagementStates.SELECT_VALUE)


@router.message(MembershipManagementStates.SELECT_VALUE)
async def process_membership(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    request = data.get("request")
    if message.text.casefold() == _("decline").casefold():
        await bot.send_message(
            chat_id=request["request"].chat_id,
            text=_("membership_not_added_member"),
            reply_markup=main_buttons(user_id=message.from_user.id)
        )
    else:
        value = int(message.text)
        member_tg_id = request["request"].tg_id
        member_name = request["member"].name
        membership = db_mb_for_admin.add_membership(tg_id=member_tg_id, membership_value=value)
        await message.answer(
            text=_("membership_added_admin").format(membership.total_amount, member_name),
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=request["request"].chat_id,
            text=_("membership_added_member").format(membership.total_amount)
        )
    db_mb_for_admin.delete_membership_request(request=request["request"])
    await state.clear()
