from datetime import date, timedelta

import allure
import pytest

import config_reader
from src.model.membership import Membership
from src.utils import translation

_ = translation.i18n.gettext


@allure.tag("positive")
@allure.feature("check-in")
def test_membership_can_subtract():
    mb = Membership(tg_id=1, total_amount=4)
    old_amount = mb.current_amount
    total_amount = mb.total_amount
    mb.subtract()
    assert mb.current_amount == old_amount - 1
    assert mb.total_amount == total_amount


@allure.tag("positive")
@allure.feature("freeze", "unfreeze")
def test_membership_freezing_and_unfreezing_delays_expiry():
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    freeze_duration = 7
    mb.freeze(freeze_date=mb.activation_date, days=freeze_duration)
    assert mb.expiry_date == mb.original_expiry_date + timedelta(days=freeze_duration)
    assert mb.unfreeze_date == mb.activation_date + timedelta(days=freeze_duration)

    new_expiry_date = mb.original_expiry_date + timedelta(days=freeze_duration)
    unfreeze_date = mb.activation_date + timedelta(days=freeze_duration)
    mb.unfreeze(unfreeze_date=unfreeze_date)
    assert mb.expiry_date == new_expiry_date


@allure.tag("positive")
@allure.feature("unfreeze")
@pytest.mark.parametrize(
    "delta", [2, -2], ids=["later than planned", "earlier than planned"]
)
def test_membership_can_unfreeze_earlier_or_later_than_planned(delta):
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    freeze_date = mb.activation_date + timedelta(days=5)
    planned_freeze_duration = 7
    mb.freeze(freeze_date=freeze_date, days=planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=actual_freeze_duration)
    mb.unfreeze(unfreeze_date=unfreeze_date)
    assert mb.expiry_date == new_expiry_date


@allure.tag("negative")
@allure.feature("freeze")
def test_membership_cannot_freeze_two_times():
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    freeze_duration = 7
    mb.freeze(days=freeze_duration)

    unfreeze_date = mb.activation_date + timedelta(days=freeze_duration)
    mb.unfreeze(unfreeze_date)
    with pytest.raises(ValueError) as error:
        mb.freeze(freeze_date=mb.activation_date, days=freeze_duration)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_second_freeze")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_membership_cannot_unfreeze_to_make_freeze_period_invalid():
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    planned_freeze_duration = 7
    mb.freeze(days=planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration - 10
    unfreeze_date = mb.activation_date + timedelta(days=actual_freeze_duration)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze(unfreeze_date=unfreeze_date)
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_unfreeze_before_freeze")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_membership_cannot_freeze_before_activation():
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(freeze_date=mb.activation_date - timedelta(days=1), days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_freeze_before_activation")


@allure.tag("negative")
@allure.feature("freeze")
def test_membership_cannot_freeze_for_over_max_duration():
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    planned_freeze_duration = 15
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(freeze_date=mb.activation_date, days=planned_freeze_duration)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_duration_exceeded").format(
        days=config_reader.config.max_freeze_duration
    )


@allure.tag("negative")
@allure.feature("check_in")
def test_membership_cannot_subtract_from_expired_membership():
    mb = Membership(tg_id=1, total_amount=4)
    mb._activate(activation_date=date.today() - timedelta(days=31))
    with pytest.raises(expected_exception=ValueError) as error:
        mb.subtract()
    assert error.value.args[0] == _("CHECK_IN_error_cannot_subtract")


@allure.tag("negative")
@allure.feature("check-in")
def test_membership_cannot_subtract_from_used_up_membership():
    mb = Membership(tg_id=1, total_amount=1)
    mb.subtract()
    with pytest.raises(expected_exception=ValueError) as error:
        mb.subtract()
    assert error.value.args[0] == _("CHECK_IN_error_cannot_subtract")


@allure.tag("negative")
@allure.feature("freeze")
def test_cannot_freeze_if_inactive():
    mb = Membership(tg_id=1, total_amount=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_not_active")


@allure.tag("negative")
@allure.feature("freeze")
def test_cannot_freeze_if_frozen():
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_already_frozen")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_cannot_unfreeze_if_not_frozen():
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze()
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_not_frozen")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_cannot_unfreeze_before_freeze():
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze(unfreeze_date=date.today() - timedelta(days=1))
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_unfreeze_before_freeze")


@allure.tag("negative")
@allure.feature("freeze")
def test_cannot_make_negative_freeze_duration_with_unfreeze():
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=2)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze(unfreeze_date=date.today() - timedelta(days=3))
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_unfreeze_before_freeze")
