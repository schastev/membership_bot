from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.membership import Membership
from src.model.request import MembershipRequest
from src.utils.database import ENGINE, get_memberships_by_tg_id


def view_memberships_by_user_id(tg_id: int) -> List[Membership]:
    with Session(ENGINE) as session:
        memberships = session.scalars(get_memberships_by_tg_id(tg_id=tg_id)).all()
    return memberships


def request_to_add_membership(tg_id: int, chat_id: int) -> MembershipRequest:
    with Session(ENGINE) as session:
        request = MembershipRequest(tg_id=tg_id, chat_id=chat_id)
        session.add(request)
        session.commit()
    with Session(ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.tg_id == tg_id)
        request = session.scalars(query).first()
    assert request is not None
    return request