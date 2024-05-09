import pytest
from aiogram_tests import MockedRequester
from aiogram_tests.handler import CallbackQueryHandler
from aiogram_tests.types.dataset import CALLBACK_QUERY, USER, CHAT
from magic_filter import F

import config_reader
from src.utils import translation
from src.utils.bot_helpers import IsAdmin
from src.utils.callback_factories import MBRequestValueCallbackFactory
from src.utils.constants import Modifier, Action
from src.utils.translation import locale
from tests.helper import get_random_locale, extract_keyboard_entries, get_user

_ = translation.i18n.gettext
config_reader.config.database_file_name = ""


_ = translation.i18n.gettext


@pytest.mark.asyncio
async def test_process_membership():
    from src.db_calls.member import request_to_add_membership
    from src.routers.mb_for_admin import process_membership
    random_locale = get_random_locale()
    user, mb = get_user(with_membership=False, locale=random_locale)
    request = request_to_add_membership(tg_id=user.tg_id, chat_id=CHAT.get("id"))
    handler = CallbackQueryHandler(
        process_membership,
        MBRequestValueCallbackFactory.filter(),
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    requester = MockedRequester(handler)
    callback_query = CALLBACK_QUERY.as_object(
        data=MBRequestValueCallbackFactory(
            member_tg_id=user.tg_id,
            member_name=user.name,
            value=10,
            chat_id=CHAT.get("id"),
            id=request.id,
        ).pack(),
        from_user=USER.as_object(id=config_reader.config.admin_ids[0]),
    )
    calls = await requester.query(callback_query)
    answer_messages = sorted(
        [message.text for message in calls.send_message.fetchall()]
    )
    assert answer_messages == [
        _("ADD_MEMBERSHIP_ok_admin", locale=random_locale).format(
            mb_value=10, member_name=user.name
        ),
        _("ADD_MEMBERSHIP_ok_member", locale=random_locale).format(mb_value=10),
    ]


@pytest.mark.asyncio
async def test_poll_for_mb_add_request():
    random_locale = get_random_locale()
    from src.routers.mb_for_admin import poll_for_mb_add_request
    from src.db_calls.member import request_to_add_membership
    test_function, request_adding_function, action, pending_message, button_name = (
        poll_for_mb_add_request,
        request_to_add_membership,
        Action.ADD_MEMBERSHIP,
        _("pending_membership", locale=random_locale),
        _("ADD_MEMBERSHIP_button", locale=random_locale),
    )
    user, mb = get_user(with_membership=False, locale=random_locale)
    first_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    first_requester = MockedRequester(first_handler)
    callback_query = CALLBACK_QUERY.as_object(
        data=f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        from_user=USER.as_object(id=config_reader.config.admin_ids[0]),
    )
    calls = await first_requester.query(callback_query)
    first_answer = sorted(
        [message.text for message in calls.send_message.fetchall()]
    )
    assert first_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("polling_timeout", locale=random_locale).format(button_name=button_name),
    ])
    request_adding_function(tg_id=user.tg_id, chat_id=CHAT.get("id"))
    second_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    second_requester = MockedRequester(second_handler)
    second_call = await second_requester.query(callback_query)
    second_answer = sorted(
        [message.text for message in second_call.send_message.fetchall()]
    )
    assert second_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("pending_list", locale=random_locale).format(request_type=pending_message),
    ])
    kb = extract_keyboard_entries(second_call.send_message.fetchall()[1].reply_markup.inline_keyboard)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}"


@pytest.mark.asyncio
async def test_poll_for_mb_freeze_request():
    random_locale = get_random_locale()
    from src.routers.mb_for_admin import poll_for_mb_freeze_request
    from src.db_calls.member import request_to_freeze_membership
    test_function, request_adding_function, action, pending_message, button_name = (
        poll_for_mb_freeze_request,
        request_to_freeze_membership,
        Action.FREEZE_MEMBERSHIP,
        _("pending_freeze", locale=random_locale),
        _("FREEZE_MEMBERSHIP_button", locale=random_locale),
    )
    user, membership = get_user(with_membership=True, locale=random_locale)
    first_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    first_requester = MockedRequester(first_handler)
    callback_query = CALLBACK_QUERY.as_object(
        data=f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        from_user=USER.as_object(id=config_reader.config.admin_ids[0]),
    )
    calls = await first_requester.query(callback_query)
    first_answer = sorted(
        [message.text for message in calls.send_message.fetchall()]
    )
    assert first_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("polling_timeout", locale=random_locale).format(button_name=button_name),
    ])
    request_adding_function(tg_id=user.tg_id, chat_id=CHAT.get("id"), mb_id=membership.id, duration=10)
    second_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    second_requester = MockedRequester(second_handler)
    second_call = await second_requester.query(callback_query)
    second_answer = sorted(
        [message.text for message in second_call.send_message.fetchall()]
    )
    assert second_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("pending_list", locale=random_locale).format(request_type=pending_message),
    ])
    kb = extract_keyboard_entries(second_call.send_message.fetchall()[1].reply_markup.inline_keyboard)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}: 10"


@pytest.mark.asyncio
async def test_manage_attendances():
    random_locale = get_random_locale()
    from src.routers.att_for_admin import manage_attendances
    from src.db_calls.member import request_to_add_attendance
    test_function, request_adding_function, action, pending_message, button_name = (
        manage_attendances,
        request_to_add_attendance,
        Action.CHECK_IN,
        _("pending_attendance", locale=random_locale),
        _("CHECK_IN_button", locale=random_locale),

    )
    user, membership = get_user(with_membership=True, locale=random_locale)
    first_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    first_requester = MockedRequester(first_handler)
    callback_query = CALLBACK_QUERY.as_object(
        data=f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        from_user=USER.as_object(id=config_reader.config.admin_ids[0]),
    )
    calls = await first_requester.query(callback_query)
    first_answer = sorted(
        [message.text for message in calls.send_message.fetchall()]
    )
    assert first_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("polling_timeout", locale=random_locale).format(button_name=button_name),
    ])
    request_adding_function(tg_id=user.tg_id, chat_id=CHAT.get("id"), mb_id=membership.id)
    second_handler = CallbackQueryHandler(
        test_function,
        F.data == f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}",
        IsAdmin(),
        state_data={"locale": random_locale},
        dp_middlewares=[locale],
    )
    second_requester = MockedRequester(second_handler)
    second_call = await second_requester.query(callback_query)
    second_answer = sorted(
        [message.text for message in second_call.send_message.fetchall()]
    )
    assert second_answer == sorted([
        _("polling", locale=random_locale).format(
            request_type_string=pending_message,
            timeout_seconds=config_reader.config.polling_timeout_seconds,
            button_name=button_name,
        ),
        _("pending_list", locale=random_locale).format(request_type=pending_message),
    ])
    kb = extract_keyboard_entries(second_call.send_message.fetchall()[1].reply_markup.inline_keyboard)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}"


