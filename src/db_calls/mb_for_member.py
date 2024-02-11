from typing import List, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.membership import Membership
from src.model.request import MembershipRequest
from src.db_calls import database


def view_memberships_by_user_id(tg_id: int) -> List[Membership]:
    with Session(database.ENGINE) as session:
        memberships = session.scalars(database.get_memberships_by_tg_id(tg_id=tg_id)).all()
    return memberships


def get_active_membership_by_user_id(tg_id: int) -> Union[Membership, None]:
    with Session(database.ENGINE) as session:
        memberships = session.scalars(database.get_memberships_by_tg_id(tg_id=tg_id)).all()
    active_mb = [mb for mb in memberships if mb.is_valid()]
    if len(active_mb) == 0:
        return None
    return active_mb[0]


def request_to_add_membership(tg_id: int, chat_id: int) -> MembershipRequest:
    with Session(database.ENGINE) as session:
        request = MembershipRequest(tg_id=tg_id, chat_id=chat_id)
        session.add(request)
        session.commit()
    with Session(database.ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.tg_id == tg_id)
        request = session.scalars(query).one()
    assert request is not None
    return request
