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
    tg_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    purchase_date: Mapped[date] = date.today()
    activation_date: Mapped[Optional[date]]
    expiry_date: Mapped[Optional[date]]
    original_expiry_date: Mapped[Optional[date]]
    _frozen: Mapped[Optional[bool]] = None
    freeze_date: Mapped[Optional[date]]
    unfreeze_date: Mapped[Optional[date]]
    total_amount: Mapped[int]
    current_amount: Mapped[Optional[int]]

    def __init__(self, tg_id: int, **kw: Any):
        super().__init__(**kw)
        self.purchase_date = date.today()
        self.current_amount = self.total_amount
        self.tg_id = tg_id

    def __repr__(self):
        return (
            f"Membership("
            f"total_amount={self.total_amount}, "
            f"current_amount={self.current_amount}, "
            f"activation_date={self.activation_date}, "
            f"purchase_date={self.purchase_date})"
        )

    def __str__(self):
        text = _("MB_INFO_general").format(
            mb_purchase_date=self.purchase_date, mb_total_amount=self.total_amount
        )
        if self.activation_date:
            text += "\n"
            text += _("MB_INFO_active").format(
                mb_rmn_value=self.current_amount,
                mb_act_date=self.activation_date,
                mb_exp_date=self.expiry_date,
            )
            if self.freeze_date:
                text += "\n"
                text += _("MB_INFO_frozen").format(
                    mb_freeze_date=self.freeze_date, mb_unfreeze_date=self.unfreeze_date
                )
        return text

    def freeze(self, days: int, freeze_date: date = date.today()) -> None:
        if self.is_valid_freeze_date(days=days):
            self._frozen = True
            self.freeze_date = freeze_date
            self.unfreeze_date = freeze_date + timedelta(days=days)
            self.expiry_date += timedelta(days=days)

    def is_valid_freeze_date(self, days: int) -> bool:
        if not self.activation_date:
            raise ValueError(_("FREEZE_MEMBERSHIP_error_not_active"))
        if days > config_reader.config.max_freeze_duration:
            raise ValueError(
                _("FREEZE_MEMBERSHIP_error_duration_exceeded").format(
                    days=config_reader.config.max_freeze_duration
                )
            )
        if days <= 0:
            raise ValueError(_("FREEZE_MEMBERSHIP_error_negative_duration"))
        if self._frozen is False:
            raise ValueError(_("FREEZE_MEMBERSHIP_error_second_freeze"))
        if self._frozen is True:
            raise ValueError(_("FREEZE_MEMBERSHIP_error_already_frozen"))
        return True

    def unfreeze(self, unfreeze_date: date = date.today()) -> None:
        if self.is_valid_unfreeze_date(unfreeze_date=unfreeze_date):
            self.unfreeze_date = unfreeze_date
            self._frozen = False
            new_expiry_date = self.original_expiry_date + (
                unfreeze_date - self.freeze_date
            )
            if self.expiry_date != new_expiry_date:
                self.expiry_date = new_expiry_date

    def is_valid_unfreeze_date(self, unfreeze_date: date = date.today()) -> bool:
        if not self._frozen:
            raise ValueError(_("UNFREEZE_MEMBERSHIP_error_not_frozen"))
        if self.unfreeze_date <= self.freeze_date:
            raise ValueError(_("UNFREEZE_MEMBERSHIP_error_unfreeze_before_freeze"))
        new_expiry_date = self.original_expiry_date + (unfreeze_date - self.freeze_date)
        if new_expiry_date - self.original_expiry_date > timedelta(days=14):
            raise ValueError(_("FREEZE_MEMBERSHIP_error_duration_exceeded"))
        if (new_expiry_date - self.original_expiry_date).days < 0:
            raise ValueError(_("FREEZE_MEMBERSHIP_error_negative_duration"))
        return True

    def subtract(self) -> None:
        if not self.activation_date:
            self._activate(date.today())
        if not self.is_valid():
            raise ValueError(_("CHECK_IN_error_cannot_subtract"))
        self.current_amount -= 1
        if self.current_amount == 0:
            self.expiry_date = date.today()
        if self.activation_date is None:
            self._activate(activation_date=date.today())
            self._frozen = False
        if self._frozen:
            self.unfreeze(unfreeze_date=date.today())

    def _activate(self, activation_date: date) -> None:
        self.activation_date = activation_date
        self.expiry_date = activation_date + timedelta(
            days=config_reader.config.membership_duration_days
        )
        self.original_expiry_date = activation_date + timedelta(
            days=config_reader.config.membership_duration_days
        )

    def is_valid(self) -> bool:
        return self.has_uses() and not self.is_expired()

    def is_expired(self) -> bool:
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    def has_uses(self) -> bool:
        return self.current_amount > 0

    def past_info(self):
        return _("MB_INFO_past").format(
            total=self.total_amount,
            act_date=self.activation_date,
            exp_date=self.expiry_date,
        )
