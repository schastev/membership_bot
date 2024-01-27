from aiogram import F, Router
from aiogram.types import CallbackQuery

import translation
from src.utils import db_mb_for_admin, db_mb_for_member
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_view_mb")
async def view_memberships(callback: CallbackQuery):
    membership_list = db_mb_for_member.view_memberships_by_user_id(tg_id=callback.from_user.id)
    if len(membership_list) == 0:
        text = _("no_memberships")
    else:
        membership = membership_list[0]
        purchase_date = membership.purchase_date
        activation_date = membership.activation_date or _("mb_inactive")
        expiry_date = membership.expiry_date or _("mb_inactive")
        current_amount = membership.current_amount
        text = _("membership_info").format(purchase_date, activation_date, expiry_date, current_amount)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_add_mb")
async def request_to_add_membership(callback: CallbackQuery):
    existing_requests = db_mb_for_admin.check_existing_requests(tg_id=callback.from_user.id)
    if len(existing_requests) == 0:
        db_mb_for_member.request_to_add_membership(tg_id=callback.from_user.id, chat_id=callback.message.chat.id)
        text = _("request_sent")
    else:
        text = _("request_already_existed")
    await callback.message.answer(text=text, reply_markup=main_buttons(user_id=callback.from_user.id))
    # todo rm buttons
    await callback.answer()
