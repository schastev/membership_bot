"""All of these are stubs until I figure out the database stuff"""
from config_reader import config


def register_user(tg_id: int, name: str, phone: str):
    pass


def update_name(tg_id: int, new_name: str):
    pass


def update_phone(tg_id: int, new_phone: str):
    pass


def check_user_registration_state(tg_id: int) -> bool:
    return True


def check_admin(tg_id: int) -> bool:
    return tg_id in config.admin_ids
