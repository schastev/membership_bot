from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.attendance import Attendance
from src.model.request import AttendanceRequest
from src.db_calls import database, mb_for_member


def view_attendances_by_user_id(tg_id: int) -> List[Attendance]:
    with Session(database.ENGINE) as session:
        attendances = session.scalars(database.get_attendances_by_tg_id(tg_id=tg_id)).all()
    return attendances


def view_attendances_for_active_membership(tg_id: int) -> List[Attendance]:
    with Session(database.ENGINE) as session:
        active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=tg_id)
        query = select(Attendance).where(Attendance.membership_id == active_mb.id)
        return session.scalars(query).all()


def request_to_add_attendance(tg_id: int, chat_id: int) -> AttendanceRequest:
    with Session(database.ENGINE) as session:
        request = AttendanceRequest(tg_id=tg_id, chat_id=chat_id)
        session.add(request)
        session.commit()
    with Session(database.ENGINE) as session:
        query = select(AttendanceRequest).where(AttendanceRequest.tg_id == tg_id)
        request = session.scalars(query).first()
    assert request is not None
    return request
