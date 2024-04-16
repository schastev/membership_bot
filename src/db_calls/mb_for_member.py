from typing import List, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.membership import Membership
from src.model.request import Request, RequestType
from src.db_calls import database


def get_memberships_by_user_id(tg_id: int) -> List[Membership]:
    with Session(database.ENGINE) as session:
        memberships = session.scalars(database.get_memberships_by_tg_id(tg_id=tg_id)).all()
    return list(memberships)


def get_active_membership_by_user_id(tg_id: int) -> Union[Membership, None]:
    with Session(database.ENGINE) as session:
        memberships = session.scalars(database.get_memberships_by_tg_id(tg_id=tg_id)).all()
    active_mb = [mb for mb in memberships if mb.is_valid()]
    if len(active_mb) == 0:
        return None
    return active_mb[0]


def request_to_add_membership(tg_id: int, chat_id: int) -> Request:
    with Session(database.ENGINE) as session:
        request = Request(tg_id=tg_id, chat_id=chat_id, type=RequestType.ADD_MEMBERSHIP, mb_id=-1, duration=-1)
        session.add(request)
        session.commit()
    with Session(database.ENGINE) as session:
        query = select(Request).where(Request.tg_id == tg_id)
        request = session.scalars(query).one()
    assert request is not None
    return request


def request_to_freeze_membership(tg_id: int, chat_id: int, mb_id: int, duration: int) -> Request:
    with Session(database.ENGINE) as session:
        request = Request(
            tg_id=tg_id, chat_id=chat_id, mb_id=mb_id, duration=duration, type=RequestType.FREEZE_MEMBERSHIP
        )
        session.add(request)
        session.commit()
    with Session(database.ENGINE) as session:
        query = select(Request).where(Request.tg_id == tg_id)
        request = session.scalars(query).one()
    assert request is not None
    return request


def unfreeze_membership(mb_id: int):
    with Session(database.ENGINE) as session:
        query = select(Membership).where(Membership.id == mb_id)
        mb = session.scalars(query).first()
        mb.unfreeze()
        session.commit()
