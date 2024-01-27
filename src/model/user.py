from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class User(Base):
    __tablename__ = "user"
    tg_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    phone: Mapped[int] = mapped_column(Numeric(11))
    language: Mapped[str]

    def __repr__(self):
        return f"User(tg_id={self.tg_id}, name={self.name}, phone={self.phone}, lang={self.language})"
