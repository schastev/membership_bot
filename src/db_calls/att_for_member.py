from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.attendance import Attendance
from src.model.request import AttendanceRequest
from src.db_calls import database


def view_attendances_by_user_id(tg_id: int) -> List[Attendance]:
    with Session(database.ENGINE) as session:
        memberships = session.scalars(database.get_attendances_by_tg_id(tg_id=tg_id)).all()
    return memberships


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
