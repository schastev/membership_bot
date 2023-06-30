from copy import deepcopy
from datetime import date, timedelta
from typing import Union

import pytest

from db import DataBase, Membership


# TODO move helper functions to the helper file
def mb_activate(mb: Membership, activation_date: date = date.today()):
    mb._activate(activation_date)
    assert mb.expiry_date == activation_date + timedelta(days=30)


def mb_freeze(mb: Membership, freeze_date: date, freeze_duration: int):
    mb._freeze_with_date(freeze_date=freeze_date, days=freeze_duration)
    assert mb.expiry_date == mb.original_expiry_date + timedelta(days=freeze_duration)
    assert mb.unfreeze_date == freeze_date + timedelta(days=freeze_duration)


def mb_unfreeze(mb: Membership, unfreeze_date: date, new_expiry_date: date):
    mb._unfreeze_with_date(unfreeze_date=unfreeze_date)
    assert mb.expiry_date == new_expiry_date


def mb_subtract(mb: Membership, activation_date: Union[date, None] = None):
    old_amount = mb.current_amount
    total_amount = mb.total_amount
    mb.subtract()
    assert mb.current_amount == old_amount - 1
    assert mb.total_amount == total_amount
    if activation_date:
        assert mb.activation_date == activation_date


def db_add(db: DataBase, mb: Membership):
    deepcopy_one = deepcopy(mb)
    old_len = len(db.memberships)
    db.add_membership(deepcopy_one)
    assert len(db.memberships) == old_len + 1
    return deepcopy_one


def test_membership_freezing_and_unfreezing_delays_expiry():
    mb = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    freeze_duration = 7
    unfreeze_date = freeze_date + timedelta(days=freeze_duration)
    mb_freeze(mb, freeze_date, freeze_duration)

    new_expiry_date = mb.original_expiry_date + timedelta(days=freeze_duration)
    mb_unfreeze(mb, unfreeze_date, new_expiry_date)


def test_membership_cannot_freeze_two_times():
    mb = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    freeze_duration = 7
    mb_freeze(mb, freeze_date, freeze_duration)

    unfreeze_date = freeze_date + timedelta(days=freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=freeze_duration)
    mb_unfreeze(mb, unfreeze_date, new_expiry_date)
    with pytest.raises(ValueError):
        mb_freeze(mb, freeze_date, freeze_duration)


@pytest.mark.parametrize("delta", [2, -2], ids=["later than planned", "earlier than planned"])
def test_membership_can_unfreeze_earlier_or_later_than_planned(delta):
    mb = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date + timedelta(days=5)
    planned_freeze_duration = 7
    mb_freeze(mb, freeze_date, planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=actual_freeze_duration)
    mb_unfreeze(mb, unfreeze_date=unfreeze_date, new_expiry_date=new_expiry_date)


@pytest.mark.parametrize("delta", [15, -15], ids=["over two weeks", "negative freeze period"])
def test_membership_cannot_unfreeze_to_make_freeze_period_invalid(delta):
    mb = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    planned_freeze_duration = 7
    mb_freeze(mb, freeze_date, planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=actual_freeze_duration)
    with pytest.raises(expected_exception=ValueError):
        mb_unfreeze(mb, unfreeze_date=unfreeze_date, new_expiry_date=new_expiry_date)


def test_membership_cannot_freeze_for_over_two_weeks():
    mb = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    planned_freeze_duration = 15
    with pytest.raises(expected_exception=ValueError):
        mb_freeze(mb, freeze_date, planned_freeze_duration)


def test_database_update():
    mb_one = Membership(member_nickname="123", total_amount=8)
    mb_two = Membership(member_nickname="234", total_amount=8)
    db = DataBase()
    deepcopy_one = db_add(db, mb_one)
    db_add(db, mb_two)

    mb_activate(mb_one, date.today())
    db.update_membership(old_membership=deepcopy_one, new_membership=mb_one)
    assert db.memberships[1] == mb_one
    assert len(db.memberships) == 2


def test_membership_can_subtract():
    md = Membership(member_nickname="123", total_amount=4)
    mb_subtract(md, activation_date=date.today())


def test_membership_can_subtract_from_activated_membership():
    md = Membership(member_nickname="123", total_amount=4)
    activation_date = date.today() - timedelta(days=10)
    mb_activate(md, activation_date=activation_date)
    mb_subtract(md, activation_date)


def test_membership_cannot_subtract_from_expired_membership():
    md = Membership(member_nickname="123", total_amount=4)
    mb_activate(md, activation_date=date.today() - timedelta(days=31))
    with pytest.raises(expected_exception=ValueError):
        md.subtract()


def test_membership_cannot_subtract_from_used_up_membership():
    md = Membership(member_nickname="123", total_amount=1)
    mb_activate(md)
    md.subtract()
    with pytest.raises(expected_exception=ValueError):
        md.subtract()




