from sqlalchemy import create_engine, select

from src.model.attendance import Attendance
from src.model.declarative_models import Base
from src.model.membership import Membership
from src.model.request import MembershipRequest, AttendanceRequest
from src.model.user import User

ENGINE = create_engine("sqlite+pysqlite:///mb_bot.db", echo=True)


Base.metadata.create_all(bind=ENGINE)


def get_user_by_tg_id(tg_id: int):
    return select(User).where(User.tg_id == tg_id)


def get_memberships_by_tg_id(tg_id: int):
    return select(Membership).where(Membership.member_id == tg_id)


def get_membership_by_id(membership_id: int):
    return select(Membership).where(Membership.id == membership_id)


def get_membership_requests_for_user(tg_id: int):
    return select(MembershipRequest).where(MembershipRequest.tg_id == tg_id)


def get_attendances_by_tg_id(tg_id: int):
    return select(Attendance).where(Attendance.member_id == tg_id)


def get_attendance_requests_for_user(tg_id: int):
    return select(AttendanceRequest).where(AttendanceRequest.tg_id == tg_id)
