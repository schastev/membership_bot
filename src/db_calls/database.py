from sqlalchemy import create_engine, select

from src.model.declarative_models import Base
from src.model.membership import Membership
from src.model.attendance import Attendance
from src.model.user import User

ENGINE = create_engine("sqlite+pysqlite:///mb_bot.db", echo=True)


Base.metadata.create_all(bind=ENGINE)


def get_user_by_tg_id(tg_id: int):
    return select(User).where(User.tg_id == tg_id)


def get_memberships_by_tg_id(tg_id: int):
    return select(Membership).where(Membership.member_id == tg_id)


def get_attendances_by_tg_id(tg_id: int):
    return select(Attendance).where(Attendance.member_id == tg_id)
