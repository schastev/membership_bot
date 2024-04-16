from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class RequestType:
    ADD_MEMBERSHIP = "ADD_MEMBERSHIP"
    FREEZE_MEMBERSHIP = "FREEZE_MEMBERSHIP"
    ATTENDANCE = "ATTENDANCE"


class Request(Base):
    __tablename__ = "request"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    mb_id: Mapped[Optional[int]] = mapped_column(ForeignKey("membership.id"))
    chat_id: Mapped[int]
    duration: Mapped[int]

    def __repr__(self):
        return f"Request(tg_id={self.tg_id}, type={self.type}{f', duration={self.duration}' if self.duration else ''})"

