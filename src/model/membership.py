from datetime import date, timedelta
from typing import Optional, Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

import config_reader
from src.model.declarative_models import Base
from src.utils import translation

_ = translation.i18n.gettext


class Membership(Base):
    __tablename__ = "membership"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    purchase_date: Mapped[date] = date.today()
    activation_date: Mapped[Optional[date]]
    expiry_date: Mapped[Optional[date]]
    original_expiry_date: Mapped[Optional[date]]
    _frozen: Mapped[Optional[bool]] = None
    freeze_date: Mapped[Optional[date]]
    unfreeze_date: Mapped[Optional[date]]
    total_amount: Mapped[int]
    current_amount: Mapped[Optional[int]]

    def __init__(self, member_id: int, **kw: Any):
        super().__init__(**kw)
        self.purchase_date = date.today()
        self.current_amount = self.total_amount
        self.member_id = member_id

    def __repr__(self):
        return f"Membership(" \
               f"total_amount={self.total_amount}, " \
               f"current_amount={self.current_amount}, " \
               f"activation_date={self.activation_date}, " \
               f"purchase_date={self.purchase_date})"

    def __str__(self):  #todo i18n this
        text = f"{_('active_mb_info')}:" \
            f"{_('mb_purchase_date')}: {self.purchase_date}\n" \
            f"{_('mb_total_amount')}: {self.total_amount}\n"
        if self.activation_date:
            text = text + f"{_('mb_rmn_value')}: {self.current_amount}\n" \
                          f"{_('mb_act_date')}: {self.activation_date}\n" \
                          f"{_('mb_exp_date')}: {self.expiry_date}\n"
            if self.freeze_date:
                text += (f"{_('mb_freeze_date')}: {self.freeze_date}\n"
                         f"{_('mb_unfreeze_date')}: {self.unfreeze_date}\n")
        else:
            text = text + "This membership has not been activated yet, so activation/expiry date is not set yet."
        return text

    def freeze(self, days: int, freeze_date: date = date.today()) -> None:
        if days > 14:
            raise ValueError("Заморозить абонемент можно не более чем на две недели.")
        if days <= 0:
            raise ValueError("Не положительная продолжительность периода заморозки.")
        if self._frozen is not None:
            raise ValueError("Заморозить один абонемент можно только один раз.")
        self._frozen = True
        self.freeze_date = freeze_date
        self.unfreeze_date = freeze_date + timedelta(days=days)
        self.expiry_date += timedelta(days=days)

    def unfreeze(self, unfreeze_date: date = date.today()) -> None:
        if not self._frozen:
            raise ValueError("Указанный абонемент не был заморожен.")
        if self.unfreeze_date <= self.freeze_date:
            raise ValueError("Дата разморозки должна быть позже даты заморозки.")
        self.unfreeze_date = unfreeze_date
        self._frozen = False
        new_expiry_date = self.original_expiry_date + (unfreeze_date - self.freeze_date)
        if new_expiry_date - self.original_expiry_date > timedelta(days=14):
            raise ValueError("Заморозить абонемент можно не более чем на две недели.")
        if (new_expiry_date - self.original_expiry_date).days <= 0:
            raise ValueError("Не положительная продолжительность периода заморозки.")
        if self.expiry_date != new_expiry_date:
            self.expiry_date = new_expiry_date

    def subtract(self) -> None:
        if not self.activation_date:
            self._activate(date.today())
        if not self.is_valid():
            raise ValueError("Абонемент полностью использован или истек срок его действия.")
        self.current_amount -= 1
        if self.activation_date is None:
            self._activate(activation_date=date.today())
            self._frozen = False

    def _activate(self, activation_date: date) -> None:
        self.activation_date = activation_date
        self.expiry_date = activation_date + timedelta(days=config_reader.config.membership_duration_days)
        self.original_expiry_date = activation_date + timedelta(days=config_reader.config.membership_duration_days)

    def is_valid(self) -> bool:
        return self.has_uses() and not self.is_expired()

    def is_expired(self) -> bool:
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    def has_uses(self) -> bool:
        return self.current_amount > 0
