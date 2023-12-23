from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
# import src.utils.membership_management as sub_management_utils

from config_reader import config

router = Router()
current_locale = config


@router.message(Command(current_locale.manage_button))
@router.message(F.text.casefold() == current_locale.manage_button)
async def manage_subscriptions(message: Message, state: FSMContext):
    await message.answer("Here we'll have a sub management menu")


@router.message(Command(current_locale.view_memberships_button))
@router.message(F.text.casefold() == current_locale.view_memberships_button)
async def manage_subscriptions(message: Message, state: FSMContext):
    # membership_list = sub_management_utils.view_user_memberships(tg_id=message.from_user.id)
    await message.answer(current_locale.membership_info.format([]))

