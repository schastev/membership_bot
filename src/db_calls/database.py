from sqlalchemy import create_engine, select

import config_reader
from src.model.declarative_models import Base
from src.model.membership import Membership
from src.model.user import User
from src.utils.decorators import singleton


@singleton
class Database:
    engine = create_engine(
        f"sqlite+pysqlite:///{config_reader.config.database_file_name}", echo=True
    )

    def __init__(self):
        Base.metadata.create_all(bind=self.engine)


def get_user_by_tg_id(tg_id: int):
    return select(User).where(User.tg_id == tg_id)


def get_memberships_by_tg_id(tg_id: int):
    return select(Membership).where(Membership.member_id == tg_id)
