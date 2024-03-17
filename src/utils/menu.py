from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils import translation
from config_reader import config
from src.utils.callback_factories import MBRequestListCallbackFactory, MBRequestValueCallbackFactory, \
    AttRequestCallbackFactory, FreezeRequestCallbackFactory
from src.db_calls import user as db_calls_user

_ = translation.i18n.gettext

admin = {"manage_button": "button_manage", "manage_att_button": "button_manage_att"}
registered_without_active_mb = {"add_membership": "button_add_mb"}
registered_with_active_mb = {
    "view_active_membership_button": "button_view_active_mb",
    "view_memberships_button": "button_view_mb",
    "add_attendance": "button_add_att",
}
registered_with_attendances = {"view_attendances_button": "button_view_att"}
registered = {
    "change_name_button": "button_change_name",
    "change_phone_button": "button_change_phone",
    "change_locale_button": "change_locale_button",
}
not_registered = {"register_button": "button_register"}


def locale_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.add(InlineKeyboardButton(text=locale, callback_data=locale)) for locale in config.locales]
    return builder.as_markup()


def main_buttons(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    user_is_registered = db_calls_user.check_user_registration_state(tg_id=user_id)
    user_is_admin = db_calls_user.is_admin(tg_id=user_id)
    user_has_usable_mb, mb_is_active, mb_is_frozen = db_calls_user.membership_status(tg_id=user_id)
    user_has_attendances = False
    buttons = {}
    if user_has_usable_mb:
        user_has_attendances = db_calls_user.has_attendances(tg_id=user_id)
    if user_is_admin:
        buttons.update(admin)
    if user_is_registered:
        buttons.update({"change_user_settings_button": "button_change_user_settings"})
        if user_has_usable_mb:
            buttons.update(registered_with_active_mb)
        elif mb_is_active:
            buttons.update({"freeze_membership": "button_freeze_mb"})
        elif mb_is_frozen:
            buttons.update({"unfreeze_mb_button": "button_unfreeze_mb"})
        else:
            buttons.update(registered_without_active_mb)
        if user_has_attendances:
            buttons.update(registered_with_attendances)
    else:
        buttons.update(not_registered)

    for k, v in buttons.items():
        builder.add(InlineKeyboardButton(text=_(k), callback_data=v))
    builder.adjust(2)
    return builder.as_markup()


def user_settings_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for k, v in registered.items():
        builder.add(InlineKeyboardButton(text=_(k), callback_data=v))
    builder.adjust(2)
    return builder.as_markup()


def mb_management_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=_("add_mb"), callback_data="button_add_mb_request"))
    builder.add(InlineKeyboardButton(text=_("freeze_mb"), callback_data="button_freeze_mb_request"))
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


def freeze_membership_request_buttons(request_list: List[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for request in request_list:
        text = f'{request["member"].name}: {int(request["member"].phone)}: {request.get("request").duration}'
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=FreezeRequestCallbackFactory(
                    member_tg_id=request.get("member").tg_id,
                    member_name=request.get("member").name,
                    membership_id=request.get("request").mb_id,
                    chat_id=request.get("request").chat_id,
                    id=request.get("request").id,
                    duration=request.get("request").duration,
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
