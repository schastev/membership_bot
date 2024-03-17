from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class MembershipRequest(Base):
    __tablename__ = "membership_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    chat_id: Mapped[int]

    def __repr__(self):
        return f"Mb_request(tg_id={self.tg_id}, chat_id={self.chat_id})"


class AttendanceRequest(Base):
    __tablename__ = "attendance_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    chat_id: Mapped[int]

    def __repr__(self):
        return f"Att_request(tg_id={self.tg_id}, chat_id={self.chat_id})"


class FreezeRequest(Base):
    __tablename__ = "freeze_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    mb_id: Mapped[int] = mapped_column(ForeignKey("membership.id"))
    chat_id: Mapped[int]
    duration: Mapped[int]

    def __repr__(self):
        return f"Freeze_request(tg_id={self.tg_id}, chat_id={self.chat_id}, duration={self.duration})"
