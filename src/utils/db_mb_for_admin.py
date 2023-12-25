import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.membership import Membership
from src.model.request import MembershipRequest
from src.model.user import User
from src.utils.database import ENGINE, get_memberships_by_tg_id, get_membership_requests_for_user


TIMER = config.polling_timeout_seconds


def check_existing_requests(tg_id: int) -> List[MembershipRequest]:
    with Session(ENGINE) as session:
        requests = session.scalars(get_membership_requests_for_user(tg_id=tg_id)).all()
    return requests


async def poll_for_membership_requests() -> list:
    query_for_requests = select(MembershipRequest)
    result = []
    timer = TIMER
    with Session(ENGINE) as session:
        requests = session.scalars(query_for_requests).all()
        while len(requests) == 0 and timer > 0:
            requests = session.scalars(query_for_requests).all()
            timer = timer - 10
            time.sleep(10)
        for request in requests:
            query_for_requesting_members = select(User).where(User.tg_id == request.tg_id)
            member = session.scalars(query_for_requesting_members).first()
            result.append({"request": request, "member": member})
    return result


def add_membership(tg_id: int, membership_value: int) -> Membership:
    with Session(ENGINE) as session:
        membership = Membership(member_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    with Session(ENGINE) as session:
        added_membership = session.scalars(get_memberships_by_tg_id(tg_id=tg_id)).one()
    return added_membership


def decline_membership_request(request: dict) -> None:
    with Session(ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.id == request.id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()
