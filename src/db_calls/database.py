from sqlalchemy import create_engine

from config_reader import GlobalSettings
from src.model.declarative_models import Base
from src.utils.decorators import singleton


@singleton
class Database:
    engine = create_engine(
        f"sqlite+pysqlite:///{GlobalSettings().config.database_file_name}", echo=False
    )

    def __init__(self):
        Base.metadata.create_all(bind=self.engine)
