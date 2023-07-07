from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.model.declarative_models import Base, Membership, User


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


engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

with Session(engine) as session:
    memb = Membership(total_amount=8)
    memb.subtract()
    user_a = User(tg_name="k_emiko", phone_number="123", memberships=[memb])
    session.add(user_a)
    session.commit()
    result = select(User)
    for user in session.scalars(result):
        print(user)
    result_two = select(Membership)
    for m in session.scalars(result_two):
        print(m)
