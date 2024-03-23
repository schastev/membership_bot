from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.attendance import Attendance
from src.model.membership import Membership
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def mark_attendance(attendance: Attendance, request_id: int) -> int:
    with Session(database.ENGINE) as session:
        session.add(attendance)
        membership_query = select(Membership).where(Membership.id == attendance.membership_id)
        membership = session.scalars(membership_query).first()
        membership.subtract()
        session.commit()
        current_amount = membership.current_amount
    from src.db_calls.for_admin import delete_request
    delete_request(request_id=request_id)
    return current_amount
