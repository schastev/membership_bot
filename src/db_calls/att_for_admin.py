import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.attendance import Attendance
from src.model.membership import Membership
from src.model.request import AttendanceRequest
from src.model.user import User
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def check_existing_attendance_requests(tg_id: int) -> List[AttendanceRequest]:
    with Session(database.ENGINE) as session:
        query = select(AttendanceRequest).where(AttendanceRequest.tg_id == tg_id)
        requests = session.scalars(query).all()
    return requests


async def poll_for_attendance_requests() -> list:
    result = []
    timer = TIMER
    with Session(database.ENGINE) as session:
        requests = session.query(AttendanceRequest, User).join(User).filter(AttendanceRequest.tg_id == User.tg_id).all()
        while len(requests) == 0 and timer > 0:
            requests = session.query(AttendanceRequest).join(User).filter(AttendanceRequest.tg_id == User.tg_id).all()
            timer = timer - 10
            time.sleep(10)
    [result.append({"request": request[0], "member": request[1]}) for request in requests]
    return result


def mark_attendance(tg_id: int, membership_id: int, request_id: int) -> None:
    with Session(database.ENGINE) as session:
        attendance = Attendance(member_id=tg_id, membership_id=membership_id)
        session.add(attendance)
        membership_query = select(Membership).where(Membership.id == membership_id)
        membership = session.scalars(membership_query).first()
        membership.subtract()
        session.commit()
    delete_attendance_request(request_id=request_id)


def delete_attendance_request(request_id: int) -> None:
    with Session(database.ENGINE) as session:
        query = select(AttendanceRequest).where(AttendanceRequest.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()
