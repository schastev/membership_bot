from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    # date: Mapped[date] = "" #date.today()
    member_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    membership_id: Mapped[int] = mapped_column(ForeignKey("membership.id"))
