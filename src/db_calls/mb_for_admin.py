import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.membership import Membership
from src.model.request import MembershipRequest, FreezeRequest
from src.model.user import User
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def check_existing_requests(tg_id: int) -> List[MembershipRequest]:
    with Session(database.ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.tg_id == tg_id)
        requests = session.scalars(query).all()
    return requests


def check_existing_freeze_requests(tg_id: int) -> List[FreezeRequest]:
    with Session(database.ENGINE) as session:
        query = select(FreezeRequest).where(FreezeRequest.tg_id == tg_id)
        requests = session.scalars(query).all()
    return requests


async def poll_for_add_mb_requests() -> list:
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


async def poll_for_freeze_mb_requests() -> list:
    result = []
    timer = TIMER
    with Session(database.ENGINE) as session:
        requests = session.query(FreezeRequest, User).join(User).filter(FreezeRequest.tg_id == User.tg_id).all()
        while len(requests) == 0 and timer > 0:
            requests = session.query(FreezeRequest).join(User).filter(FreezeRequest.tg_id == User.tg_id).all()
            timer = timer - 10
            time.sleep(10)
    [result.append({"request": request[0], "member": request[1]}) for request in requests]
    return result


def add_membership(tg_id: int, membership_value: int, request_id: int) -> None:
    with Session(database.ENGINE) as session:
        membership = Membership(member_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    delete_membership_request(request_id=request_id)


def delete_membership_request(request_id: int) -> None:
    with Session(database.ENGINE) as session:
        query = select(MembershipRequest).where(MembershipRequest.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()


def freeze_membership(mb_id: int, days: int, request_id: int):
    with Session(database.ENGINE) as session:
        query = select(Membership).where(Membership.id == mb_id)
        mb = session.scalars(query).first()
        mb.freeze(days=days)
        session.commit()
    delete_freeze_mb_request(request_id=request_id)


def delete_freeze_mb_request(request_id: int) -> None:
    with Session(database.ENGINE) as session:
        query = select(FreezeRequest).where(FreezeRequest.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()
