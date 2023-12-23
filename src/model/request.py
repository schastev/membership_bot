from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class MembershipRequest(Base):
    __tablename__ = "membership_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    chat_id: Mapped[int]

    def __repr__(self):
        return f"M_request(tg_id={self.tg_id}, chat_id={self.chat_id})"
