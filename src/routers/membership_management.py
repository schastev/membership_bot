from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup
import src.utils.membership_management as mb_management_utils
from project import BOT
from src.utils import menu_utils

from config_reader import config
from src.utils.menu_utils import compile_membership_value_list_menu
from src.utils.user_actions import check_admin

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
    membership_addition_requests = mb_management_utils.poll_for_membership_requests()
    if len(membership_addition_requests) == 0:
        await message.answer(locale.polling_timeout)
    else:
        await state.update_data(requests=membership_addition_requests)
        membership_request_buttons = menu_utils.compile_membership_request_list_menu(membership_addition_requests)
        await message.answer(
            text="Here are pending membership requests:",
            reply_markup=ReplyKeyboardMarkup(keyboard=[membership_request_buttons], resize_keyboard=True)
        )
        await state.set_state(MembershipManagementStates.SELECT_MEMBER)


@router.message(Command(locale.view_membership_button))
@router.message(F.text.casefold() == locale.view_membership_button.casefold())
async def view_memberships(message: Message):
    membership_list = mb_management_utils.view_memberships_by_user_id(tg_id=message.from_user.id)
    if len(membership_list) == 0:
        text = locale.no_memberships
    else:
        text = locale.membership_info.format(membership_list)
    await message.answer(text)


@router.message(Command(locale.add_membership))
@router.message(F.text.casefold() == locale.add_membership.casefold())
async def request_to_add_membership(message: Message, state: FSMContext):
    mb_management_utils.request_to_add_membership(tg_id=message.from_user.id)
    await message.answer(locale.request_sent)


@router.message(MembershipManagementStates.SELECT_MEMBER)
async def add_membership_select_member(message: Message, state: FSMContext):
    data = await state.get_data()
    requests = data.get("requests")
    member_name, member_phone = message.text.split(": ")
    request = [r for r in requests if r["name"] == member_name and r["phone"] == member_phone]
    await state.update_data(request_tg_id=request[0]["tg_id"])
    await state.update_data(request=request[0])
    membership_values = compile_membership_value_list_menu()
    await message.answer(
        text="Please select membership value from the list below:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[membership_values], resize_keyboard=True)
    )
    await state.set_state(MembershipManagementStates.SELECT_VALUE)


@router.message(MembershipManagementStates.SELECT_VALUE)
async def add_membership_select_value(message: Message, state: FSMContext):
    data = await state.get_data()
    value = int(message.text)
    request = data.get("request")
    member_tg_id = request.get("tg_id")
    member_name = request["name"]
    mb_management_utils.add_membership(tg_id=member_tg_id, membership_value=value)
    await message.answer(text=f"Membership with value {value} for {member_name} added successfully.")
    await BOT.send_message(chat_id=request["chat_id"], text=f"A membership with value {value} wa added for you.")
    await state.clear()

