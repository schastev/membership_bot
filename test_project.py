from datetime import date, timedelta
from typing import Union

import pytest
from sqlalchemy.orm import Session

from db import DataBase
from src.model.declarative_models import Membership, User


# TODO move helper functions to the helper file


@pytest.fixture()
def database():
    db = DataBase()
    yield db
    with Session(db.engine) as session:
        session.close()


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


def test_membership_freezing_and_unfreezing_delays_expiry():
    mb = Membership(total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    freeze_duration = 7
    unfreeze_date = freeze_date + timedelta(days=freeze_duration)
    mb_freeze(mb, freeze_date, freeze_duration)

    new_expiry_date = mb.original_expiry_date + timedelta(days=freeze_duration)
    mb_unfreeze(mb, unfreeze_date, new_expiry_date)


def test_membership_cannot_freeze_two_times():
    mb = Membership(total_amount=4)
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
    mb = Membership(total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date + timedelta(days=5)
    planned_freeze_duration = 7
    mb_freeze(mb, freeze_date, planned_freeze_duration)

    actual_freeze_duration = planned_freeze_duration + delta
    unfreeze_date = freeze_date + timedelta(days=actual_freeze_duration)
    new_expiry_date = mb.original_expiry_date + timedelta(days=actual_freeze_duration)
    mb_unfreeze(mb, unfreeze_date=unfreeze_date, new_expiry_date=new_expiry_date)


@pytest.mark.parametrize("delta", [8, -7], ids=["over two weeks", "negative freeze period"])
def test_membership_cannot_unfreeze_to_make_freeze_period_invalid(delta):
    mb = Membership(total_amount=4)
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
    mb = Membership(total_amount=4)
    activation_date = date.today()
    mb_activate(mb, activation_date)

    freeze_date = activation_date - timedelta(days=5)
    planned_freeze_duration = 15
    with pytest.raises(expected_exception=ValueError):
        mb_freeze(mb, freeze_date, planned_freeze_duration)


def test_database_update(database):
    mb_one = Membership(total_amount=8)
    mb_two = Membership(total_amount=8)
    user = User(tg_name="sdsgsfds", memberships=[mb_one, mb_two])
    with Session(database.engine) as session_one:
        session_one.add(user)
        mb_activate(mb_one, date.today())
        database.update_item(mb_one, session_one)
        session_one.commit()
    with Session(database.engine) as session_two:
        all_memberships = database.all_items(mb_one, session_two)
        assert all_memberships[0].activation_date == date.today()
        assert all_memberships[1].activation_date is None
        assert len(all_memberships) == 2


def test_membership_can_subtract():
    md = Membership(total_amount=4)
    mb_subtract(md, activation_date=date.today())


def test_membership_can_subtract_from_activated_membership():
    md = Membership(total_amount=4)
    activation_date = date.today() - timedelta(days=10)
    mb_activate(md, activation_date=activation_date)
    mb_subtract(md, activation_date)


def test_membership_cannot_subtract_from_expired_membership():
    md = Membership(total_amount=4)
    mb_activate(md, activation_date=date.today() - timedelta(days=31))
    with pytest.raises(expected_exception=ValueError):
        md.subtract()


def test_membership_cannot_subtract_from_used_up_membership():
    md = Membership(total_amount=1)
    mb_activate(md)
    md.subtract()
    with pytest.raises(expected_exception=ValueError):
        md.subtract()
