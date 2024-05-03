import pytest
from aiogram_tests import MockedRequester
from aiogram_tests.handler import CallbackQueryHandler
from aiogram_tests.types.dataset import CALLBACK_QUERY, USER

import config_reader
from src.db_calls.mb_for_member import request_to_add_membership
from src.routers.mb_for_admin import process_membership
from src.utils import translation
from src.utils.bot_helpers import IsAdmin
from src.utils.callback_factories import MBRequestValueCallbackFactory


_ = translation.i18n.gettext


@pytest.mark.asyncio
async def test_process_membership():
    request = request_to_add_membership(tg_id=123, chat_id=321)
    requester = MockedRequester(
        CallbackQueryHandler(
            process_membership, MBRequestValueCallbackFactory.filter(), IsAdmin()
        )
    )
    callback_query = CALLBACK_QUERY.as_object(
        data=MBRequestValueCallbackFactory(
            member_tg_id=123,
            member_name="test_user_name",
            value=10,
            chat_id=321,
            id=request.id,
        ).pack(),
        from_user=USER.as_object(id=config_reader.config.admin_ids[0]),
    )
    calls = await requester.query(callback_query)
    answer_messages = sorted(
        [message.text for message in calls.send_message.fetchall()]
    )
    assert answer_messages == [
        _("ADD_MEMBERSHIP_ok_admin").format(mb_value=10, member_name="test_user_name"),
        _("ADD_MEMBERSHIP_ok_member").format(mb_value=10),
    ]
