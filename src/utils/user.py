"""All of these are stubs until I figure out the database stuff"""
from sqlalchemy.orm import Session

from config_reader import config

from src.model.user import User
from src.utils.database import ENGINE, get_user_by_tg_id


def register_user(tg_id: int, name: str, phone: str) -> User:
    with Session(ENGINE) as session:
        user = User(name=name, phone=phone, tg_id=tg_id)
        session.add(user)
        session.commit()
    with Session(ENGINE) as session:
        added_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
    return added_user


def update_name(tg_id: int, new_name: str) -> User:
    with Session(ENGINE) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        user.name = new_name
        session.commit()
    with Session(ENGINE) as session:
        updated_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        assert updated_user.name == new_name
    return updated_user


def update_phone(tg_id: int, new_phone: int) -> User:
    with Session(ENGINE) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        user.phone = new_phone
        session.commit()
    with Session(ENGINE) as session:
        updated_user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).one()
        assert int(updated_user.phone) == new_phone
    return updated_user


def check_user_registration_state(tg_id: int) -> bool:
    with Session(ENGINE) as session:
        user = session.scalars(get_user_by_tg_id(tg_id=tg_id)).first()
    if user:
        return True
    else:
        return False


def check_admin(tg_id: int) -> bool:
    return tg_id in config.admin_ids
