from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config_reader import config
from src.utils import db_mb_for_admin, db_mb_for_member
from src.utils.misc import FullMenuMarkup

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
        text = locale.membership_info.format(
            membership.purchase_date, membership.activation_date, membership.expiry_date, membership.current_amount
        )
    await message.answer(text, reply_markup=FullMenuMarkup(user_id=message.from_user.id))


@router.message(Command(locale.add_membership))
@router.message(F.text.casefold() == locale.add_membership.casefold())
async def request_to_add_membership(message: Message):
    existing_requests = db_mb_for_admin.check_existing_requests(tg_id=message.from_user.id)
    if len(existing_requests) == 0:
        db_mb_for_member.request_to_add_membership(tg_id=message.from_user.id, chat_id=message.chat.id)
        await message.answer(text=locale.request_sent, reply_markup=FullMenuMarkup(user_id=message.from_user.id))
    else:
        await message.answer(
            text=locale.request_already_existed, reply_markup=FullMenuMarkup(user_id=message.from_user.id)
        )
