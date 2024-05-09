from random import Random

import pytest
from aiogram_tests.types.dataset import USER, CHAT


@pytest.fixture
def db_calls():
    from src import db_calls

    return db_calls


@pytest.fixture
def routers():
    from src import routers

    return routers


@pytest.fixture
def utils():
    from src import utils

    return utils


@pytest.fixture
def get_user(db_calls):
    created_user = []

    def _wrapper(with_membership: bool, locale: str):
        user_id = Random().randint(0, 999999999)
        user = db_calls.user.register_user(
            tg_id=user_id, name=USER.get("username"), phone=str(user_id), locale=locale
        )
        membership = None
        if with_membership:
            request = db_calls.member.request_to_add_membership(
                tg_id=user.tg_id, chat_id=CHAT.get("id")
            )
            db_calls.admin.add_membership(
                tg_id=user.tg_id, membership_value=10, request_id=request.id
            )
            membership = db_calls.member.get_active_membership_by_user_id(
                tg_id=user.tg_id
            )
            created_user.append(user)
        return user, membership

    yield _wrapper
    if created_user:
        db_calls.user.delete_user(tg_id=created_user[0].tg_id)
