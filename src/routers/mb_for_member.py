from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.utils import translation
from src.db_calls import mb_for_member, mb_for_admin
from src.utils.menu import main_buttons

router = Router()
_ = translation.i18n.gettext


@router.callback_query(F.data == "button_view_mb")
async def view_memberships(callback: CallbackQuery):
    active_membership = mb_for_member.get_active_membership_by_user_id(tg_id=callback.from_user.id)
    if not active_membership:
        text = _("no_memberships")
    else:
        purchase_date = active_membership.purchase_date
        activation_date = active_membership.activation_date or _("mb_inactive")
        expiry_date = active_membership.expiry_date or _("mb_inactive")
        current_amount = active_membership.current_amount
        text = _("membership_info").format(purchase_date, activation_date, expiry_date, current_amount)
    await callback.message.answer(text, reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "button_add_mb")
async def request_to_add_membership(callback: CallbackQuery):
    existing_requests = mb_for_admin.check_existing_requests(tg_id=callback.from_user.id)
    if len(existing_requests) == 0:
        mb_for_member.request_to_add_membership(tg_id=callback.from_user.id, chat_id=callback.message.chat.id)
        text = _("request_sent_mb")
    else:
        text = _("request_already_existed")
    await callback.message.answer(text=text, reply_markup=main_buttons(user_id=callback.from_user.id))
    # todo rm buttons
    await callback.answer()
