from typing import List

from sqlalchemy.orm import Session

from src.model.membership import Membership
from src.utils.database import ENGINE, get_memberships_by_tg_id


def view_memberships_by_user_id(tg_id: int) -> List[Membership]:
    with Session(ENGINE) as session:
        memberships = session.scalars(get_memberships_by_tg_id(tg_id=tg_id)).all()
    return memberships


def request_to_add_membership(tg_id: int) -> None:
    add_membership(tg_id=tg_id, membership_value=8)
    # todo this is for debug purposes, make some sort of storage for requests


def poll_for_membership_resolution(tg_id: int) -> Membership:
    # fixme this is for debug, add a 1-minute poll
    # todo add filters by active membership
    return view_memberships_by_user_id(tg_id=tg_id)[0]


def poll_for_membership_requests() -> list:
    # fixme this is for debug, add a 1-minute poll, also make some sort of storage for requests
    return [
        {"tg_id": 256981966, "name": "Jane", "phone": "1234", "chat_id": 256981966},
        {"tg_id": 256981966, "name": "Alice", "phone": "5678", "chat_id": 256981966}
    ]


def add_membership(tg_id: int, membership_value: int) -> Membership:
    with Session(ENGINE) as session:
        membership = Membership(member_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    with Session(ENGINE) as session:
        added_membership = session.scalars(get_memberships_by_tg_id(tg_id=tg_id)).one()
    return added_membership
