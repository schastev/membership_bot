from typing import Union

from sqlalchemy.orm import Session

from config_reader import config

from src.model.user import User
from src.db_calls import mb_for_member, att_for_member, database


def register_user(tg_id: int, name: str, phone: str, locale: str) -> User:
    with Session(database.ENGINE) as session:
        user = User(name=name, phone=phone, tg_id=tg_id, locale=locale)
        session.add(user)
        session.commit()
    with Session(database.ENGINE) as session:
        added_user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
    return added_user


def update_name(tg_id: int, new_name: str) -> User:
    with Session(database.ENGINE) as session:
        user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        user.name = new_name
        session.commit()
    with Session(database.ENGINE) as session:
        updated_user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        assert updated_user.name == new_name
    return updated_user


def update_phone(tg_id: int, new_phone: int) -> User:
    with Session(database.ENGINE) as session:
        user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        user.phone = new_phone
        session.commit()
    with Session(database.ENGINE) as session:
        updated_user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        assert int(updated_user.phone) == new_phone
    return updated_user


def update_user_locale(tg_id: int, new_locale: str) -> User:
    with Session(database.ENGINE) as session:
        user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        user.locale = new_locale
        session.commit()
    with Session(database.ENGINE) as session:
        updated_user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).one()
        assert updated_user.locale == new_locale
    return updated_user


def check_user_registration_state(tg_id: int) -> Union[User, None]:
    with Session(database.ENGINE) as session:
        user = session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).first()
    if user:
        return user
    else:
        return None


def get_user(tg_id: int) -> Union[User, None]:
    with Session(database.ENGINE) as session:
        return session.scalars(database.get_user_by_tg_id(tg_id=tg_id)).first()
