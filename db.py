from typing import Union

from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session

from src.model.declarative_models import Base, Membership, User


class DataBase:  # witness my brilliant stub and marvel at its ingeniousness
    engine: Engine

    def __init__(self) -> None:
        self.engine = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(self.engine)

    def add_item(self, item: Union["Membership", "User"]) -> None:
        with Session(self.engine) as session:
            session.add(item)
            session.commit()

    def remove_item(self, item: Union["Membership", "User"]) -> None:
        with Session(self.engine) as session:
            session.delete(item)
            session.commit()

    def update_item(self, item: Union["Membership", "User"], ses: Session = None):
        close_session = False
        if ses is None:
            close_session = True
            ses = Session(self.engine)
        query = select(type(item)).where(type(item).id == item.id)
        memb = ses.scalar(query)
        memb = item
        if close_session:
            ses.close()

    def all_items(self, item: Union["Membership", "User"], ses: Session = None):
        close_session = False
        if ses is None:
            close_session = True
            ses = Session(self.engine)
        query = select(type(item))
        if close_session:
            ses.close()
        return ses.scalars(query).all()
