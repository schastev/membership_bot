from datetime import date

from babel.dates import format_date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.declarative_models import Base


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    attendance_date: Mapped[date] = date.today()
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    membership_id: Mapped[int] = mapped_column(ForeignKey("membership.id"))

    def print(self, locale: str):
        return format_date(self.attendance_date, locale=locale)
