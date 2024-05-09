import datetime
from random import Random

import pytest

from config_reader import GlobalSettings
from src.model.membership import Membership
from src.utils.constants import Action, Modifier, MenuButtons
from project import main_menu
from src.utils.menu import UserState
from tests.helper import extract_keyboard_entries

_ = GlobalSettings().i18n.gettext


def test_main_buttons_not_registered():
    user_state = UserState(tg_id=0)
    is_admin = Random().choice([True, False])
    user_state.is_admin = is_admin
    keyboard = main_menu(user_id=0, user_state=user_state)
    buttons = extract_keyboard_entries(keyboard)
    expected = [Action.REGISTER]
    if is_admin:
        expected.extend(MenuButtons.ADMIN)
    assert sorted(buttons) == sorted([_(f"{ex}{Modifier.BUTTON}") for ex in expected])


def test_main_buttons_registered():
    user_state = UserState(tg_id=0)
    is_admin = Random().choice([True, False])
    user_state.is_admin = is_admin
    user_state.is_registered = True
    keyboard = main_menu(user_id=0, user_state=user_state)
    buttons = extract_keyboard_entries(keyboard)
    expected = [Action.CHANGE_SETTINGS, Action.ADD_MEMBERSHIP]
    if is_admin:
        expected.extend(MenuButtons.ADMIN)
    assert sorted(buttons) == sorted([_(f"{ex}{Modifier.BUTTON}") for ex in expected])


@pytest.mark.parametrize(
    "has_active_mb, expected",
    [
        pytest.param(
            True,
            [Action.VIEW_ACTIVE_MEMBERSHIP, Action.CHECK_IN],
            id="Has active membership",
        ),
        pytest.param(False, [Action.ADD_MEMBERSHIP], id="Has no active membership"),
    ],
)
def test_main_buttons_with_and_without_active_membership(has_active_mb, expected):
    user_state = UserState(tg_id=0)
    is_admin = Random().choice([True, False])
    user_state.is_admin = is_admin
    (
        user_state.is_registered,
        user_state.has_memberships,
        user_state.has_usable_membership,
    ) = True, True, has_active_mb
    keyboard = main_menu(user_id=0, user_state=user_state)
    buttons = extract_keyboard_entries(keyboard)
    expected = [Action.CHANGE_SETTINGS, Action.VIEW_ALL_MEMBERSHIPS, *expected]
    if is_admin:
        expected.extend(MenuButtons.ADMIN)
    assert sorted(buttons) == sorted([_(f"{ex}{Modifier.BUTTON}") for ex in expected])


@pytest.mark.parametrize(
    "frozen, unfrozen, expected",
    [
        pytest.param(
            True, False, [Action.UNFREEZE_MEMBERSHIP], id="Has a frozen membership"
        ),
        pytest.param(True, True, [], id="Has a frozen and unfrozen membership"),
    ],
)
def test_main_buttons_active_membership_states(frozen, unfrozen, expected):
    active_mb = Membership(tg_id=1, total_amount=8)
    active_mb._activate(
        activation_date=datetime.date.today() - datetime.timedelta(days=1)
    )
    if frozen:
        active_mb.freeze(
            freeze_date=datetime.date.today() - datetime.timedelta(days=1), days=10
        )
    if unfrozen:
        active_mb.unfreeze()
    user_state = UserState(tg_id=0, active_mb=active_mb)
    is_admin = Random().choice([True, False])
    has_attendances = Random().choice([True, False])
    (
        user_state.is_admin,
        user_state.is_registered,
        user_state.has_usable_membership,
        user_state.has_memberships,
        user_state.has_attendances,
    ) = is_admin, True, True, True, has_attendances
    keyboard = main_menu(user_id=0, user_state=user_state)
    buttons = extract_keyboard_entries(keyboard)
    expected = [
        Action.CHANGE_SETTINGS,
        Action.VIEW_ACTIVE_MEMBERSHIP,
        Action.CHECK_IN,
        Action.VIEW_ALL_MEMBERSHIPS,
        *expected,
    ]
    if is_admin:
        expected.extend(MenuButtons.ADMIN)
    if has_attendances:
        expected.append(Action.VIEW_ATTENDANCES)
    assert sorted(buttons) == sorted([_(f"{ex}{Modifier.BUTTON}") for ex in expected])
