from datetime import date, timedelta
from typing import Optional, List, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_name: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[Optional[str]] = mapped_column(String(11))

    memberships: Mapped[List["Membership"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, tg_name={self.tg_name}, phone_number={self.phone_number})"


class Membership(Base):
    __tablename__ = "memberships"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    purchase_date: Mapped[date] = date.today()
    activation_date: Mapped[Optional[date]]
    expiry_date: Mapped[Optional[date]]
    original_expiry_date: Mapped[Optional[date]]
    frozen: Mapped[bool] = False
    freeze_date: Mapped[Optional[date]]
    unfreeze_date: Mapped[Optional[date]]
    total_amount: Mapped[int]
    current_amount: Mapped[Optional[int]]

    user: Mapped["User"] = relationship(back_populates="memberships")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self.current_amount = self.total_amount

    def __repr__(self):
        return f"Membership(id={self.id}, " \
               f"member_id={self.member_id}, " \
               f"total_amount={self.total_amount}, " \
               f"current_amount={self.current_amount}, " \
               f"activation_date={self.activation_date}, " \
               f"purchase_date={self.purchase_date})"

    def freeze(self, days: int) -> None:
        self._freeze_with_date(date.today(), days=days)

    def unfreeze(self) -> None:
        self._unfreeze_with_date(unfreeze_date=date.today())

    def _freeze_with_date(self, freeze_date: date, days: int) -> None:
        if days > 14:
            raise ValueError("Заморозить абонемент можно не более чем на две недели.")
        if self.unfreeze_date:
            raise ValueError("Заморозить один абонемент можно только один раз.")
        self.frozen = True
        self.freeze_date = freeze_date
        self.unfreeze_date = freeze_date + timedelta(days=days)
        self.expiry_date += self.unfreeze_date - self.freeze_date

    def _unfreeze_with_date(self, unfreeze_date: date) -> None:
        if not self.frozen:
            raise ValueError("Указанный абонемент не был заморожен.")
        self.unfreeze_date = unfreeze_date
        self.frozen = False
        new_expiry_date = self.original_expiry_date + (unfreeze_date - self.freeze_date)
        if new_expiry_date - self.original_expiry_date > timedelta(days=14):
            raise ValueError("Заморозить абонемент можно не более чем на две недели.")
        if (new_expiry_date - self.original_expiry_date).days <= 0:
            raise ValueError("Не положительная продолжительность периода заморозки.")
        if self.expiry_date != new_expiry_date:
            self.expiry_date = new_expiry_date
        self.freeze_date = None

    def subtract(self) -> None:
        if not self.activation_date:
            self._activate(date.today())
        if not self._check_validity():
            raise ValueError("Абонемент полностью использован или истек срок его действия.")
        self.current_amount -= 1

    def _activate(self, activation_date: date) -> None:
        self.activation_date = activation_date
        self.expiry_date = activation_date + timedelta(days=30)
        self.original_expiry_date = activation_date + timedelta(days=30)

    def _check_validity(self) -> bool:
        return self.current_amount > 0 and self.expiry_date > date.today()
