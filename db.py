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
