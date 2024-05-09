import datetime
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.db_calls import member as db_member, user as db_user
from src.model.membership import Membership
from config_reader import GlobalSettings
from src.utils.callback_factories import (
    MBRequestListCallbackFactory,
    MBRequestValueCallbackFactory,
    AttRequestCallbackFactory,
    FreezeRequestCallbackFactory,
)
from src.utils.constants import Action, Modifier, MenuButtons

_ = GlobalSettings().i18n.gettext


class UserState:
    is_admin: bool = False
    is_registered: bool = False
    has_memberships: bool = False
    has_usable_membership: bool = False
    has_frozen_membership: bool = False
    has_freezable_membership: bool = False
    has_attendances: bool = False

    def __init__(self, tg_id: int, active_mb: Membership | None = None):
        if tg_id:
            self.is_admin = tg_id in GlobalSettings().config.admin_ids
            user = db_user.get_user(tg_id=tg_id)
            self.is_registered = bool(user)
            active_mb = active_mb or db_member.get_active_membership_by_user_id(
                tg_id=tg_id
            )
            self.has_memberships = bool(
                db_member.get_memberships_by_user_id(tg_id=tg_id)
            )
        if active_mb:
            self.has_usable_membership = True
            self.has_frozen_membership = (
                bool(active_mb.freeze_date)
                and active_mb.unfreeze_date > datetime.date.today()
            )
            self.has_freezable_membership = (
                bool(active_mb.activation_date)
                and not active_mb.unfreeze_date
                and not self.has_frozen_membership
            )
            if tg_id:
                attendances = db_member.view_attendances_for_active_membership(
                    tg_id=tg_id
                )
                self.has_attendances = bool(attendances)


def locale_buttons() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [
        builder.add(InlineKeyboardButton(text=locale, callback_data=locale))
        for locale in GlobalSettings().config.locales
    ]
    return builder.as_markup()


def main_buttons(
    user_id: int, user_state: UserState | None = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = []
    if not user_state:
        user_state = UserState(tg_id=user_id)
    if user_state.is_admin:
        buttons.extend(MenuButtons.ADMIN)
    if user_state.is_registered:
        buttons.append(Action.CHANGE_SETTINGS)
        if user_state.has_memberships:
            buttons.append(Action.VIEW_ALL_MEMBERSHIPS)
        if user_state.has_usable_membership:
            buttons.extend(MenuButtons.ACTIVE_MB)
            if user_state.has_attendances:
                buttons.extend(MenuButtons.CHECK_INS)
            if user_state.has_frozen_membership:
                buttons.append(Action.UNFREEZE_MEMBERSHIP)
            elif user_state.has_freezable_membership:
                buttons.append(Action.FREEZE_MEMBERSHIP)
        else:
            buttons.append(Action.ADD_MEMBERSHIP)
    else:
        buttons.append(Action.REGISTER)
    for button in buttons:
        builder.add(
            InlineKeyboardButton(
                text=_(
                    "{button}{modifier}".format(button=button, modifier=Modifier.BUTTON)
                ),
                callback_data=f"{button}{Modifier.CALLBACK}",
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def user_settings_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in MenuButtons.REGISTERED:
        builder.add(
            InlineKeyboardButton(
                text=_(
                    "{button}{modifier}".format(button=button, modifier=Modifier.BUTTON)
                ),
                callback_data=f"{button}{Modifier.CALLBACK}",
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def mb_management_options() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in MenuButtons.MANAGE_MB:
        builder.add(
            InlineKeyboardButton(
                text=_(
                    "{button}{modifier}".format(
                        button=button, modifier=Modifier.BUTTON
                    ).replace(Modifier.ADMIN, "")
                ),
                callback_data=f"{button}{Modifier.CALLBACK}",
            )
        )
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
                    id=request.get("request").id,
                ).pack(),
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
                ).pack(),
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
                ).pack(),
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def membership_value_buttons(
    member_tg_id: int, member_name: str, chat_id: int, request_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    membership_values = GlobalSettings().config.membership_values
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
                ).pack(),
            )
        )
    builder.add(
        InlineKeyboardButton(
            text=_("ADD_MEMBERSHIP_decline_button"),
            callback_data=MBRequestValueCallbackFactory(
                member_tg_id=member_tg_id,
                member_name=member_name,
                value=-1,
                chat_id=chat_id,
                id=request_id,
            ).pack(),
        )
    )
    builder.adjust(2)
    return builder.as_markup()


def cancel_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=_("button_cancel"), callback_data=f"{Action.CANCEL}{Modifier.CALLBACK}"
        )
    )
    return builder.as_markup()
