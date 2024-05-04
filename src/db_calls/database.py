from sqlalchemy import create_engine

import config_reader
from src.model.declarative_models import Base


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Database:
    engine = create_engine(
        f"sqlite+pysqlite:///{config_reader.config.database_file_name}", echo=True
    )

    def __init__(self):
        Base.metadata.create_all(bind=self.engine)
