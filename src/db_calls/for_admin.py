import time
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db_calls import database
from src.db_calls.mb_for_admin import TIMER
from src.model.request import RequestType, Request
from src.model.user import User


def check_existing_requests(tg_id: int, request_type: RequestType) -> List[Request]:
    with Session(database.ENGINE) as session:
        query = select(Request).where((Request.tg_id == tg_id) and (Request.type == request_type))
        requests = session.scalars(query).all()
    return requests


async def poll_for_requests(request_type: RequestType) -> list:
    result = []
    timer = TIMER
    with Session(database.ENGINE) as session:
        requests = session.query(Request, User).join(User).filter((Request.tg_id == User.tg_id) and (Request.type == request_type)).all()
        while len(requests) == 0 and timer > 0:
            requests = session.query(Request).join(User).filter(Request.tg_id == User.tg_id).all()
            timer = timer - 10
            time.sleep(10)
    [result.append({"request": request[0], "member": request[1]}) for request in requests]
    return result


def delete_request(request_id: int) -> None:
    with Session(database.ENGINE) as session:
        query = select(Request).where(Request.id == request_id)
        db_request = session.scalars(query).first()
        session.delete(db_request)
        session.commit()
