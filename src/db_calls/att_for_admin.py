from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.attendance import Attendance
from src.model.membership import Membership
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def mark_attendance(tg_id: int, membership_id: int, request_id: int) -> None:
    with Session(database.ENGINE) as session:
        attendance = Attendance(member_id=tg_id, membership_id=membership_id)
        session.add(attendance)
        membership_query = select(Membership).where(Membership.id == membership_id)
        membership = session.scalars(membership_query).first()
        membership.subtract()
        session.commit()
    from src.db_calls.for_admin import delete_request
    delete_request(request_id=request_id)
