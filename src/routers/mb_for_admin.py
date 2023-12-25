from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from src.utils import menu, db_mb_for_admin

from config_reader import config
from src.utils.menu import main_buttons
from src.utils.db_user import check_admin

router = Router()
locale = config


class MembershipManagementStates(StatesGroup):
    SELECT_MEMBER = State()
    SELECT_VALUE = State()


@router.message(Command(locale.manage_button))
@router.message(F.text.casefold() == locale.manage_button.casefold())
async def manage_memberships(message: Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        await message.answer(locale.not_admin)
        return
    await message.answer(locale.polling.format(config.polling_timeout_seconds))
    requests = await db_mb_for_admin.poll_for_membership_requests()
    if len(requests) == 0:
        await message.answer(locale.polling_timeout)
    else:
        await state.update_data(requests=requests)
        request_buttons = menu.membership_request_buttons(requests)
        await message.answer(
            text=locale.pending_requests,
            reply_markup=ReplyKeyboardMarkup(keyboard=[request_buttons], resize_keyboard=True)
        )
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
        text=locale.select_value,
        reply_markup=ReplyKeyboardMarkup(keyboard=[membership_values], resize_keyboard=True)
    )
    await state.set_state(MembershipManagementStates.SELECT_VALUE)


@router.message(MembershipManagementStates.SELECT_VALUE)
@router.message(F.text.casefold() == locale.decline.casefold())
async def decline_request(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    request = data.get("request")
    db_mb_for_admin.decline_membership_request(request=request["request"])
    menu_buttons = main_buttons(message.from_user.id)
    await bot.send_message(
        chat_id=request["request"].chat_id,
        text=locale.membership_not_added_member,
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(MembershipManagementStates.SELECT_VALUE)
@router.message(F.text.in_(config.membership_values))
async def add_membership_select_value(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    value = int(message.text)
    request = data.get("request")
    member_tg_id = request["request"].tg_id
    member_name = request["member"].name
    membership = db_mb_for_admin.add_membership(tg_id=member_tg_id, membership_value=value)
    await message.answer(
        text=locale.membership_added_admin.format(membership.total_amount, member_name),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
    await bot.send_message(
        chat_id=request["request"].chat_id, text=locale.membership_added_member.format(membership.total_amount)
    )
