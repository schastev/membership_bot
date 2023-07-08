from typing import Union

from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session

from src.model.declarative_models import Base, Membership, User


class DataBase:  # witness my brilliant stub and marvel at its ingeniousness
    engine: Engine

    def __init__(self) -> None:
        self.engine = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(self.engine)

    def update_item(self, item: Union["Membership", "User"], ses: Session):
        query = select(type(item)).where(type(item).id == item.id)
        memb = ses.scalar(query)
        memb = item

    def all_items(self, item: Union["Membership", "User"], ses: Session):
        query = select(type(item))
        return ses.scalars(query).all()
