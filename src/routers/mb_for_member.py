from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup

from config_reader import config
from src.utils import menu, db_mb_for_admin, db_mb_for_member

router = Router()
locale = config


@router.message(Command(locale.view_membership_button))
@router.message(F.text.casefold() == locale.view_membership_button.casefold())
async def view_memberships(message: Message):
    membership_list = db_mb_for_member.view_memberships_by_user_id(tg_id=message.from_user.id)
    if len(membership_list) == 0:
        text = locale.no_memberships
    else:
        membership = membership_list[0]
        text = f"{locale.membership_info}\n" \
               f"purchase date: {membership.purchase_date}\n" \
               f"activation date: {membership.activation_date}\n" \
               f"expiration date: {membership.expiry_date}\n" \
               f"remaining value: {membership.current_amount}\n"
    menu_buttons = menu.main_buttons(message.from_user.id)
    await message.answer(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(Command(locale.add_membership))
@router.message(F.text.casefold() == locale.add_membership.casefold())
async def request_to_add_membership(message: Message):
    existing_requests = db_mb_for_admin.check_existing_requests(tg_id=message.from_user.id)
    menu_buttons = menu.main_buttons(message.from_user.id)
    if len(existing_requests) == 0:
        db_mb_for_member.request_to_add_membership(tg_id=message.from_user.id, chat_id=message.chat.id)
        await message.answer(
            text=locale.request_sent,
            reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
        )
    else:
        await message.answer(
            text=locale.request_already_existed,
            reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
        )
