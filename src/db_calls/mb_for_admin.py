from sqlalchemy import select
from sqlalchemy.orm import Session

from config_reader import config
from src.model.membership import Membership
from src.db_calls import database


TIMER = config.polling_timeout_seconds


def add_membership(tg_id: int, membership_value: int, request_id: int) -> None:
    with Session(database.ENGINE) as session:
        membership = Membership(member_id=tg_id, total_amount=membership_value)
        session.add(membership)
        session.commit()
    from src.db_calls.for_admin import delete_request
    delete_request(request_id=request_id)


def freeze_membership(mb_id: int, days: int, request_id: int) -> str:
    with Session(database.ENGINE) as session:
        query = select(Membership).where(Membership.id == mb_id)
        mb = session.scalars(query).first()
        mb.freeze(days=days)
        unfreeze_date = mb.unfreeze_date
        session.commit()
    from src.db_calls.for_admin import delete_request
    delete_request(request_id=request_id)
    return unfreeze_date
