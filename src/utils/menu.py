from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import translation
from config_reader import config
from src.utils.callback_factories import MBRequestListCallbackFactory, MBRequestValueCallbackFactory
from src.utils.db_user import check_admin, check_user_registration_state, check_no_memberships

_ = translation.i18n.gettext


def language_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.add(InlineKeyboardButton(text=lang, callback_data=lang)) for lang in config.languages]
    return builder.as_markup()


def main_buttons(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    user_is_registered = check_user_registration_state(user_id)
    user_is_admin = check_admin(user_id)
    user_has_no_memberships = check_no_memberships(user_id)
    if user_is_admin:
        builder.add(InlineKeyboardButton(text=_("manage_button"), callback_data="button_manage"))
    if user_is_registered and user_has_no_memberships:
        builder.add(InlineKeyboardButton(text=_("add_membership"), callback_data="button_add_mb"))
    elif user_is_registered and not user_has_no_memberships:
        builder.add(InlineKeyboardButton(text=_("view_membership_button"), callback_data="button_view_mb"))
    if user_is_registered:
        builder.add(
            InlineKeyboardButton(text=_("change_name_button"), callback_data="button_change_name"),
            InlineKeyboardButton(text=_("change_phone_button"), callback_data="button_change_phone"),
            InlineKeyboardButton(text=_("change_language_button"), callback_data="button_change_language"),
        )
    else:
        builder.add(InlineKeyboardButton(text=_("register_button"), callback_data="button_register"))
    builder.adjust(2)
    return builder.as_markup()


def membership_request_buttons(request_list: List[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for request in request_list:
        text = f'{request["member"].name}: {int(request["member"].phone)}'
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=MBRequestListCallbackFactory(
                    member_tg_id=request.get("member").tg_id,
                    member_name=request.get("member").name,
                    chat_id=request.get("request").chat_id,
                    id=request.get("request").id
                ).pack()
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def membership_value_buttons(
        member_tg_id: int, member_name: str, chat_id: int, request_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    membership_values = config.membership_values
    for value in membership_values:
        builder.add(
            InlineKeyboardButton(
                text=str(value),
                callback_data=MBRequestValueCallbackFactory(
                    member_tg_id=member_tg_id,
                    member_name=member_name,
                    value=value,
                    chat_id=chat_id,
                    id=request_id,
                ).pack()))
    builder.add(
        InlineKeyboardButton(
            text=_("decline"),
            callback_data=MBRequestValueCallbackFactory(
                member_tg_id=member_tg_id,
                member_name=member_name, value=-1,
                chat_id=chat_id,
                id=request_id
            ).pack()
        )
    )
    builder.adjust(2)
    return builder.as_markup()
