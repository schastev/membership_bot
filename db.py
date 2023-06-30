from datetime import date, timedelta
from typing import Union


class DataBase:  # witness my brilliant stub and marvel at its ingeniousness
    memberships: list

    def __init__(self) -> None:
        self.memberships = []

    def add_membership(self, membership: "Membership") -> None:
        self.memberships.append(membership)

    def remove_membership(self, membership: "Membership") -> None:
        self.memberships.remove(membership)

    def update_membership(self, old_membership: "Membership", new_membership: "Membership"):
        # todo will need to replace this with select by id once I move on to an actual database
        index = self.memberships.index(old_membership)
        self.memberships.pop(index)
        self.memberships.append(new_membership)


class Membership:
    member_nickname: str
    purchase_date: date
    activation_date: Union[date, None] = None
    expiry_date: Union[date, None] = None
    original_expiry_date: Union[date, None] = None
    frozen: bool
    freeze_date: Union[date, None] = None
    unfreeze_date: Union[date, None] = None
    total_amount: int
    current_amount: int

    def __init__(self, member_nickname: str, total_amount: int) -> None:
        self.member_nickname = member_nickname
        self.total_amount = total_amount
        self.current_amount = total_amount
        self.purchase_date = date.today()

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
        if (new_expiry_date - self.original_expiry_date).days < 0:
            raise ValueError("Отрицательная продолжительность периода заморозки.")
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
