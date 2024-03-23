from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.attendance import Attendance
from src.model.request import RequestType, Request
from src.db_calls import database, mb_for_member


def view_attendances_for_active_membership(tg_id: int) -> List[Attendance]:
    with Session(database.ENGINE) as session:
        active_mb = mb_for_member.get_active_membership_by_user_id(tg_id=tg_id)
        query = select(Attendance).where(Attendance.membership_id == active_mb.id)
        return list(session.scalars(query).all())


def request_to_add_attendance(tg_id: int, chat_id: int, mb_id: int) -> Request:
    with Session(database.ENGINE) as session:
        request = Request(tg_id=tg_id, chat_id=chat_id, type=RequestType.ATTENDANCE, mb_id=mb_id, duration=-1)
        session.add(request)
        session.commit()
    with Session(database.ENGINE) as session:
        query = select(Request).where(Request.tg_id == tg_id)
        request = session.scalars(query).one()
    assert request is not None
    return request
