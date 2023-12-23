from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import src.utils.membership_management as sub_management_utils

from config_reader import config
from src.utils.user_actions import check_admin

router = Router()
current_locale = config


@router.message(Command(current_locale.manage_button))
@router.message(F.text.casefold() == current_locale.manage_button.casefold())
async def manage_memberships(message: Message, state: FSMContext):
    if check_admin(message.from_user.id):
        await message.answer("Here we'll have a sub management menu")
    else:
        await message.answer("You are not an admin!")


@router.message(Command(current_locale.view_memberships_button))
@router.message(F.text.casefold() == current_locale.view_memberships_button.casefold())
async def view_memberships(message: Message, state: FSMContext):
    membership_list = sub_management_utils.view_memberships_by_user_id(tg_id=message.from_user.id)
    await message.answer(current_locale.membership_info.format(membership_list))

