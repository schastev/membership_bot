from datetime import date, timedelta

import pytest
from src.model.membership import Membership


def test_membership_can_subtract():
    mb = Membership(total_amount=4, member_id=1)
    old_amount = mb.current_amount
    total_amount = mb.total_amount
    mb.subtract()
    assert mb.current_amount == old_amount - 1
    assert mb.total_amount == total_amount


def test_membership_freezing_and_unfreezing_delays_expiry():
    mb = Membership(total_amount=4, member_id=1)
    mb.subtract()

    freeze_date = date.today() - timedelta(days=5)
    freeze_duration = 7
    mb.freeze(freeze_date=freeze_date, days=freeze_duration)
    assert mb.expiry_date == mb.original_expiry_date + timedelta(days=freeze_duration)
    assert mb.unfreeze_date == freeze_date + timedelta(days=freeze_duration)

    new_expiry_date = mb.original_expiry_date + timedelta(days=freeze_duration)
    unfreeze_date = freeze_date + timedelta(days=freeze_duration)
    mb.unfreeze(unfreeze_date=unfreeze_date)
    assert mb.expiry_date == new_expiry_date


@pytest.mark.parametrize(
    "delta", [2, -2], ids=["later than planned", "earlier than planned"]
)
def test_membership_can_unfreeze_earlier_or_later_than_planned(delta):
    mb = Membership(total_amount=4, member_id=1)
    mb.subtract()

    freeze_date = mb.activation_date + timedelta(days=5)
    planned_freeze_duration = 7
    mb.freeze(freeze_date=freeze_date, days=planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=actual_freeze_duration)
    mb.unfreeze(unfreeze_date=unfreeze_date)
    assert mb.expiry_date == new_expiry_date


def test_membership_cannot_freeze_two_times():
    mb = Membership(total_amount=4, member_id=1)
    mb.subtract()

    freeze_date = mb.activation_date - timedelta(days=5)
    freeze_duration = 7
    mb.freeze(freeze_date=freeze_date, days=freeze_duration)

    unfreeze_date = freeze_date + timedelta(days=freeze_duration)
    mb.unfreeze(unfreeze_date)
    with pytest.raises(ValueError):
        mb.freeze(freeze_date=freeze_date, days=freeze_duration)


@pytest.mark.parametrize(
    "delta", [8, -10], ids=["over two weeks", "negative freeze period"]
)
def test_membership_cannot_unfreeze_to_make_freeze_period_invalid(delta):
    mb = Membership(total_amount=4, member_id=1)
    mb.subtract()

    freeze_date = mb.activation_date - timedelta(days=5)
    planned_freeze_duration = 7
    mb.freeze(freeze_date=freeze_date, days=planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    with pytest.raises(expected_exception=ValueError):
        mb.unfreeze(unfreeze_date=unfreeze_date)


def test_membership_cannot_freeze_for_over_two_weeks():
    mb = Membership(total_amount=4, member_id=1)
    mb.subtract()

    freeze_date = mb.activation_date - timedelta(days=5)
    planned_freeze_duration = 15
    with pytest.raises(expected_exception=ValueError):
        mb.freeze(freeze_date=freeze_date, days=planned_freeze_duration)


def test_membership_cannot_subtract_from_expired_membership():
    mb = Membership(total_amount=4, member_id=1)
    mb._activate(activation_date=date.today() - timedelta(days=31))
    with pytest.raises(expected_exception=ValueError):
        mb.subtract()


def test_membership_cannot_subtract_from_used_up_membership():
    md = Membership(total_amount=1, member_id=1)
    md.subtract()
    with pytest.raises(expected_exception=ValueError):
        md.subtract()
