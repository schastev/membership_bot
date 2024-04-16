from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils import translation
from config_reader import config
from src.utils.callback_factories import MBRequestListCallbackFactory, MBRequestValueCallbackFactory, \
    AttRequestCallbackFactory, FreezeRequestCallbackFactory
from src.db_calls import user as db_calls_user, mb_for_member, att_for_member
from src.utils.constants import Action, Modifier

_ = translation.i18n.gettext

admin = [f"{Action.MANAGE_MEMBERSHIP}", Action.MANAGE_ATTENDANCE]
registered_with_active_mb = [Action.VIEW_ACTIVE_MEMBERSHIP, Action.VIEW_ALL_MEMBERSHIPS, Action.CHECK_IN]
registered_with_attendances = [Action.VIEW_ATTENDANCES]
registered = [Action.CHANGE_NAME, Action.CHANGE_PHONE, Action.CHANGE_LOCALE]
membership_management_options = [f"{Modifier.ADMIN}{Action.ADD_MEMBERSHIP}", f"{Modifier.ADMIN}{Action.FREEZE_MEMBERSHIP}", Action.UNFREEZE_MEMBERSHIP]


class UserState:
    is_admin: bool = False
    is_registered: bool = False
    has_memberships: bool = False
    has_usable_membership: bool = False
    has_frozen_membership: bool = False
    has_freezable_membership: bool = False
    has_attendances: bool = False

    def __init__(self, tg_id: int):
        self.is_admin = tg_id in config.admin_ids
        user = db_calls_user.get_user(tg_id=tg_id)
        self.is_registered = bool(user)
        active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=tg_id)
        if active_mb:
            self.has_usable_membership = bool(active_mb)
            self.has_frozen_membership = bool(active_mb.freeze_date)
            self.has_freezable_membership = bool(active_mb.activation_date) and not self.has_frozen_membership
            attendances = att_for_member.view_attendances_for_active_membership(tg_id=tg_id)
            self.has_attendances = bool(attendances)


def locale_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.add(InlineKeyboardButton(text=locale, callback_data=locale)) for locale in config.locales]
    return builder.as_markup()


def main_buttons(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = []
    user = UserState(tg_id=user_id)
    if user.is_admin:
        buttons.extend(admin)
    if user.is_registered:
        buttons.append(Action.CHANGE_SETTINGS)
        if user.has_usable_membership:
            buttons.extend(registered_with_active_mb)
            if user.has_attendances:
                buttons.extend(registered_with_attendances)
            if user.has_frozen_membership:
                buttons.append(Action.UNFREEZE_MEMBERSHIP)
            elif user.has_freezable_membership:
                buttons.append(Action.FREEZE_MEMBERSHIP)
        else:
            buttons.append(Action.ADD_MEMBERSHIP)
    else:
        buttons.append(Action.REGISTER)
    for button in buttons:
        button_text = f"{button}{Modifier.BUTTON}"
        builder.add(InlineKeyboardButton(text=_(button_text), callback_data=f"{button}{Modifier.CALLBACK}"))
    builder.adjust(2)
    return builder.as_markup()


def user_settings_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in registered:
        button_text = f"{button}{Modifier.BUTTON}"
        builder.add(InlineKeyboardButton(text=_(button_text), callback_data=f"{button}{Modifier.CALLBACK}"))
    builder.adjust(2)
    return builder.as_markup()


def mb_management_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in membership_management_options:
        builder.add(InlineKeyboardButton(text=_("{button}{modifier}".format(button=button, modifier=Modifier.BUTTON)), callback_data=f"{button}{Modifier.CALLBACK}"))
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
                    id=request.get("request").id,
                    membership_id=request.get("request").mb_id,
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
            text=_("ADD_MEMBERSHIP_decline_button"),
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
