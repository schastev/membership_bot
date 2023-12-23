from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
import src.utils.membership as membership_utils
from src.utils import menu

from config_reader import config
from src.utils.menu import main_buttons
from src.utils.user import check_admin

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
    await message.answer(locale.polling)
    requests = membership_utils.poll_for_membership_requests()
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


@router.message(Command(locale.view_membership_button))
@router.message(F.text.casefold() == locale.view_membership_button.casefold())
async def view_memberships(message: Message):
    membership_list = membership_utils.view_memberships_by_user_id(tg_id=message.from_user.id)
    if len(membership_list) == 0:
        text = locale.no_memberships
    else:
        membership = membership_list[0]
        text = f"{locale.membership_info}\n" \
               f"purchase date: {membership.purchase_date}\n" \
               f"activation date: {membership.activation_date}\n" \
               f"expiration date: {membership.expiry_date}\n" \
               f"remaining value: {membership.current_amount}\n"
    await message.answer(text)


@router.message(Command(locale.add_membership))
@router.message(F.text.casefold() == locale.add_membership.casefold())
async def request_to_add_membership(message: Message):
    existing_requests = membership_utils.check_existing_requests(tg_id=message.from_user.id)
    if len(existing_requests) == 0:
        request = membership_utils.request_to_add_membership(tg_id=message.from_user.id, chat_id=message.chat.id)
    else:
        request = existing_requests[0]
    await message.answer(text=locale.request_sent)
    membership = membership_utils.poll_for_membership_resolution(request=request)
    menu_buttons = main_buttons(message.from_user.id)
    if membership:
        await message.answer(
            text=locale.membership_added_member.format(membership.total_amount),
            reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
        )
    else:
        await message.answer(
            text=locale.membership_not_added_member,
            reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
        )


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
async def add_membership_select_value(message: Message, state: FSMContext):
    data = await state.get_data()
    value = int(message.text)
    request = data.get("request")
    member_tg_id = request["request"].tg_id
    member_name = request["member"].name
    membership = membership_utils.add_membership(tg_id=member_tg_id, membership_value=value)
    await message.answer(
        text=locale.membership_added_admin.format(membership.total_amount, member_name),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()

