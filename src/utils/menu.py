from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils import translation
from config_reader import config
from src.utils.callback_factories import MBRequestListCallbackFactory, MBRequestValueCallbackFactory, \
    AttRequestCallbackFactory
from src.db_calls import user as db_calls_user

_ = translation.i18n.gettext


def locale_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.add(InlineKeyboardButton(text=locale, callback_data=locale)) for locale in config.locales]
    return builder.as_markup()


def main_buttons(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    user_is_registered = db_calls_user.check_user_registration_state(tg_id=user_id)
    user_is_admin = db_calls_user.is_admin(tg_id=user_id)
    user_has_memberships = db_calls_user.has_active_memberships(tg_id=user_id)
    user_has_attendances = False
    if user_has_memberships:
        user_has_attendances = db_calls_user.has_attendances(tg_id=user_id)
    if user_is_admin:
        builder.add(InlineKeyboardButton(text=_("manage_button"), callback_data="button_manage"))
        builder.add(InlineKeyboardButton(text=_("manage_att_button"), callback_data="button_manage_att"))
    if user_is_registered and not user_has_memberships:
        builder.add(InlineKeyboardButton(text=_("add_membership"), callback_data="button_add_mb"))
    elif user_is_registered and user_has_memberships:
        builder.add(InlineKeyboardButton(text=_("view_active_membership_button"), callback_data="button_view_active_mb"))
        builder.add(InlineKeyboardButton(text=_("view_memberships_button"), callback_data="button_view_mb"))
        builder.add(InlineKeyboardButton(text=_("add_attendance"), callback_data="button_add_att"))
    if user_is_registered and user_has_attendances:
        builder.add(InlineKeyboardButton(text=_("view_attendances_button"), callback_data="button_view_att"))
    if user_is_registered:
        builder.add(
            InlineKeyboardButton(text=_("change_name_button"), callback_data="button_change_name"),
            InlineKeyboardButton(text=_("change_phone_button"), callback_data="button_change_phone"),
            InlineKeyboardButton(text=_("change_locale_button"), callback_data="button_change_locale"),
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


def attendance_request_buttons(request_list: List[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for request in request_list:
        text = f'{request["member"].name}: {int(request["member"].phone)}'
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=AttRequestCallbackFactory(
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
