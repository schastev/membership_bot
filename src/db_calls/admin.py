import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.db_calls.database import Database
from src.model.attendance import Attendance
from src.model.membership import Membership
from src.model.request import RequestType, Request
from src.model.user import User


TIMER = config.polling_timeout_seconds


def check_existing_requests(tg_id: int, request_type: RequestType) -> List[Request]:
    with Session(Database().engine) as session:
        query = select(Request).where(
            (Request.tg_id == tg_id) and (Request.type == request_type)
        )
        requests = session.scalars(query).all()
    return list(requests)


async def poll_for_requests(request_type: RequestType) -> list:
    result = []
    timer = TIMER
    with Session(Database().engine) as session:
        requests = (
            session.query(Request, User)
            .join(User)
            .filter((Request.tg_id == User.tg_id) and (Request.type == request_type))
            .all()
        )
        while len(requests) == 0 and timer > 0:
            requests = (
                session.query(Request)
                .join(User)
                .filter(Request.tg_id == User.tg_id)
                .all()
            )
            timer = timer - 10
            time.sleep(10)
    [
        result.append({"request": request[0], "member": request[1]})
        for request in requests
    ]
    return result


def delete_request(request_id: int) -> None:
    with Session(Database().engine) as session:
        query = select(Request).where(Request.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()


def add_membership(tg_id: int, membership_value: int, request_id: int) -> None:
    with Session(Database().engine) as session:
        membership = Membership(tg_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    delete_request(request_id=request_id)


def freeze_membership(mb_id: int, days: int, request_id: int) -> str:
    with Session(Database().engine) as session:
        query = select(Membership).where(Membership.id == mb_id)
        mb = session.scalars(query).first()
        mb.freeze(days=days)
        unfreeze_date = mb.unfreeze_date
        session.commit()
    delete_request(request_id=request_id)
    return unfreeze_date


def mark_attendance(attendance: Attendance, request_id: int) -> int:
    with Session(Database().engine) as session:
        session.add(attendance)
        membership_query = select(Membership).where(
            Membership.id == attendance.membership_id
        )
        membership = session.scalars(membership_query).first()
        membership.subtract()
        session.commit()
        current_amount = membership.current_amount
    delete_request(request_id=request_id)
    return current_amount
