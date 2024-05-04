from typing import Union

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from src.model.attendance import Attendance
from src.model.membership import Membership
from src.model.request import Request
from src.model.user import User
from src.db_calls.database import Database


def get_user_by_tg_id(tg_id: int):
    return select(User).where(User.tg_id == tg_id)


def register_user(tg_id: int, name: str, phone: str, locale: str) -> User:
    with Session(Database().engine) as session:
        user = User(name=name, phone=phone, tg_id=tg_id, locale=locale)
        session.add(user)
        session.commit()
    with Session(Database().engine) as session:
        added_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
    return added_user


def update_name(tg_id: int, new_name: str) -> User:
    with Session(Database().engine) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        user.name = new_name
        session.commit()
    with Session(Database().engine) as session:
        updated_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        assert updated_user.name == new_name
    return updated_user


def update_phone(tg_id: int, new_phone: int) -> User:
    with Session(Database().engine) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        user.phone = new_phone
        session.commit()
    with Session(Database().engine) as session:
        updated_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        assert int(updated_user.phone) == new_phone
    return updated_user


def update_user_locale(tg_id: int, new_locale: str) -> User:
    with Session(Database().engine) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        user.locale = new_locale
        session.commit()
    with Session(Database().engine) as session:
        updated_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        assert updated_user.locale == new_locale
    return updated_user


def check_user_registration_state(tg_id: int) -> Union[User, None]:
    with Session(Database().engine) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).first()
    if user:
        return user
    else:
        return None


def get_user(tg_id: int) -> Union[User, None]:
    with Session(Database().engine) as session:
        return session.scalars(get_user_by_tg_id(tg_id=tg_id)).first()


def delete_user(tg_id: int) -> None:
    with Session(Database().engine) as session:
        session.delete(get_user(tg_id=tg_id))
        membership_query = delete(Membership).where(Membership.tg_id == tg_id)
        session.execute(membership_query)
        attendance_query = delete(Attendance).where(Attendance.tg_id == tg_id)
        session.execute(attendance_query)
        requests_query = delete(Request).where(Request.tg_id == tg_id)
        session.execute(requests_query)
        session.commit()
