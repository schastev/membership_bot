from datetime import date, timedelta

import allure
import pytest

from config_reader import GlobalSettings
from src.model.membership import Membership

_ = GlobalSettings().i18n.gettext


@allure.tag("positive")
@allure.feature("check-in")
def test_membership_can_subtract():
    """Check in with a valid memebrship."""
    mb = Membership(tg_id=1, total_amount=4)
    old_amount = mb.current_amount
    total_amount = mb.total_amount
    mb.subtract()
    assert mb.current_amount == old_amount - 1
    assert mb.total_amount == total_amount


@allure.tag("positive")
@allure.feature("freeze", "unfreeze")
def test_membership_freezing_and_unfreezing_delays_expiry():
    """Freezing delays expiry, unfreezing early updates expiry date aas well."""
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
    """Can unfreeze earlier or later than planned within max freeze duration."""
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
    """Cannot freeze a membership for a second time."""
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
def test_membership_cannot_freeze_before_activation():
    """Freeze date needs to be after activation date."""
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(freeze_date=mb.activation_date - timedelta(days=1), days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_freeze_before_activation")


@allure.tag("negative")
@allure.feature("freeze")
def test_membership_cannot_freeze_for_over_max_duration():
    """Cannot exceed max freeze duration."""
    mb = Membership(tg_id=1, total_amount=4)
    mb.subtract()

    planned_freeze_duration = 15
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(freeze_date=mb.activation_date, days=planned_freeze_duration)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_duration_exceeded").format(
        days=GlobalSettings().config.max_freeze_duration
    )


@allure.tag("negative")
@allure.feature("check_in")
def test_membership_cannot_subtract_from_expired_membership():
    """Cannot check in with expired membership."""
    mb = Membership(tg_id=1, total_amount=4)
    mb._activate(activation_date=date.today() - timedelta(days=31))
    with pytest.raises(expected_exception=ValueError) as error:
        mb.subtract()
    assert error.value.args[0] == _("CHECK_IN_error_cannot_subtract")


@allure.tag("negative")
@allure.feature("check-in")
def test_membership_cannot_subtract_from_used_up_membership():
    """Cannot check in with membership with no uses left."""
    mb = Membership(tg_id=1, total_amount=1)
    mb.subtract()
    with pytest.raises(expected_exception=ValueError) as error:
        mb.subtract()
    assert error.value.args[0] == _("CHECK_IN_error_cannot_subtract")


@allure.tag("negative")
@allure.feature("freeze")
def test_cannot_freeze_if_inactive():
    """Membership needs to be active for freeze to work."""
    mb = Membership(tg_id=1, total_amount=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_not_active")


@allure.tag("negative")
@allure.feature("freeze")
def test_cannot_freeze_if_frozen():
    """Cannot freeze membership if it's already frozen."""
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.freeze(days=1)
    assert error.value.args[0] == _("FREEZE_MEMBERSHIP_error_already_frozen")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_cannot_unfreeze_if_not_frozen():
    """Cannot unfreeze a non-frozen membership."""
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze()
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_not_frozen")


@allure.tag("negative")
@allure.feature("unfreeze")
def test_cannot_unfreeze_before_freeze():
    """Cannot use unfreeze date to make it earlier than freeze date."""
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=1)
    with pytest.raises(expected_exception=ValueError) as error:
        mb.unfreeze(unfreeze_date=date.today() - timedelta(days=1))
    assert error.value.args[0] == _("UNFREEZE_MEMBERSHIP_error_unfreeze_before_freeze")


@allure.tag("positive")
@allure.feature("freeze", "unfreeze")
@pytest.mark.parametrize(
    "freeze_duration", [1, 5], ids=["one-day freeze", "multiple-day freeze"]
)
def test_same_day_freeze_and_unfreeze_do_not_count(freeze_duration):
    """Unfreezing on the same day as freezing does not count towards one-freeze rule for memberships."""
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=freeze_duration)
    assert mb.expiry_date != mb.original_expiry_date
    mb.unfreeze()
    assert mb.freeze_date is None
    assert mb.unfreeze_date is None
    assert mb.expiry_date == mb.original_expiry_date


@allure.tag("positive")
@allure.feature("freeze")
def test_can_refreeze_after_same_day_freeze_and_unfreeze():
    """After being frozen and unfrozen on the same day the same membership can be frozen again."""
    mb = Membership(tg_id=1, total_amount=3)
    mb.subtract()
    mb.freeze(days=1)
    mb.unfreeze()
    mb.freeze(days=10)
    assert mb._frozen is True
