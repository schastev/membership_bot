import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.membership import Membership
from src.model.request import MembershipRequest
from src.model.user import User
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def check_existing_requests(tg_id: int) -> List[MembershipRequest]:
    with Session(database.ENGINE) as session:
        requests = session.scalars(database.get_membership_requests_for_user(tg_id=tg_id)).all()
    return requests


async def poll_for_membership_requests() -> list:
    result = []
    timer = TIMER
    with Session(database.ENGINE) as session:
        requests = session.query(MembershipRequest, User).join(User).filter(MembershipRequest.tg_id == User.tg_id).all()
        while len(requests) == 0 and timer > 0:
            requests = session.query(MembershipRequest).join(User).filter(MembershipRequest.tg_id == User.tg_id).all()
            timer = timer - 10
            time.sleep(10)
    [result.append({"request": request[0], "member": request[1]}) for request in requests]
    return result


def add_membership(tg_id: int, membership_value: int) -> Membership:
    with Session(database.ENGINE) as session:
        membership = Membership(member_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    with Session(database.ENGINE) as session:
        added_membership = session.scalars(database.get_memberships_by_tg_id(tg_id=tg_id)).first()
    return added_membership


def delete_membership_request(request_id: int) -> None:
    with Session(database.ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()
