import datetime


def view_memberships_by_user_id(tg_id: int) -> list:
    return [
        {
            "purchase date": str(datetime.date.today()),
            "activation date": str(datetime.date.today()),
            "expiration date": str(datetime.date.today() + datetime.timedelta(days=30)),
            "total": 4,
            "remaining": 2
        }
    ]


def request_to_add_membership(tg_id: int) -> None:
    pass


def poll_for_membership_resolution(tg_id: int) -> dict:
    return view_memberships_by_user_id(tg_id=tg_id)[0]


def poll_for_membership_requests() -> list:
    return [
        {"tg_id": 256981966, "name": "Jane", "phone": "1234", "chat_id": 256981966},
        {"tg_id": 256981966, "name": "Alice", "phone": "5678", "chat_id": 256981966}
    ]


def add_membership(tg_id: int, membership_value: int):
    pass
