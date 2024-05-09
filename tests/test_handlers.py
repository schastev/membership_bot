import pytest
from aiogram_tests.types.dataset import CHAT

from config_reader import GlobalSettings
from src.utils.callback_factories import MBRequestValueCallbackFactory
from src.utils.constants import Action
from tests import helper

_ = GlobalSettings().i18n.gettext


@pytest.mark.asyncio
async def test_process_membership(db_calls, routers, get_user):
    random_locale = helper.get_random_locale()
    user, mb = get_user(with_membership=False, locale=random_locale)
    request = db_calls.member.request_to_add_membership(
        tg_id=user.tg_id, chat_id=CHAT.get("id")
    )
    value = 10
    answer = await helper.send_mocked_message_with_factory_data_callback_admin(
        locale=random_locale,
        handler_to_mock=routers.mb_for_admin.process_membership,
        factory=MBRequestValueCallbackFactory,
        member_tg_id=user.tg_id,
        member_name=user.name,
        value=value,
        chat_id=CHAT.get("id"),
        id=request.id,
    )
    assert sorted([a.text for a in answer]) == sorted(
        [
            _("ADD_MEMBERSHIP_ok_admin", locale=random_locale).format(
                mb_value=value, member_name=user.name
            ),
            _("ADD_MEMBERSHIP_ok_member", locale=random_locale).format(mb_value=value),
        ]
    )


@pytest.mark.asyncio
async def test_poll_for_mb_add_request(db_calls, routers, get_user):
    random_locale = helper.get_random_locale()
    test_function = routers.mb_for_admin.poll_for_mb_add_request
    action = Action.ADD_MEMBERSHIP
    pending_message = _("pending_membership", locale=random_locale)
    button_name = _("ADD_MEMBERSHIP_button", locale=random_locale)
    user, mb = get_user(with_membership=False, locale=random_locale)
    polling_message = _("polling", locale=random_locale).format(
        request_type_string=pending_message,
        timeout_seconds=GlobalSettings().config.polling_timeout_seconds,
        button_name=button_name,
    )
    first_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in first_answer]) == sorted(
        [
            polling_message,
            _("polling_timeout", locale=random_locale).format(button_name=button_name),
        ]
    )
    request = db_calls.member.request_to_add_membership(
        tg_id=user.tg_id, chat_id=CHAT.get("id")
    )
    second_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in second_answer]) == sorted(
        [
            polling_message,
            _("pending_list", locale=random_locale).format(
                request_type=pending_message
            ),
        ]
    )
    kb = helper.extract_keyboard_entries(second_answer[1].reply_markup)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}"
    db_calls.admin.delete_request(request_id=request.id)


@pytest.mark.asyncio
async def test_poll_for_mb_freeze_request(db_calls, routers, get_user):
    random_locale = helper.get_random_locale()
    test_function = routers.mb_for_admin.poll_for_mb_freeze_request
    action = Action.FREEZE_MEMBERSHIP
    pending_message = _("pending_freeze", locale=random_locale)
    button_name = _("FREEZE_MEMBERSHIP_button", locale=random_locale)
    user, membership = get_user(with_membership=True, locale=random_locale)
    duration = 10
    polling_message = _("polling", locale=random_locale).format(
        request_type_string=pending_message,
        timeout_seconds=GlobalSettings().config.polling_timeout_seconds,
        button_name=button_name,
    )
    first_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in first_answer]) == sorted(
        [
            polling_message,
            _("polling_timeout", locale=random_locale).format(button_name=button_name),
        ]
    )
    db_calls.member.request_to_freeze_membership(
        tg_id=user.tg_id, chat_id=CHAT.get("id"), mb_id=membership.id, duration=duration
    )
    second_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in second_answer]) == sorted(
        [
            polling_message,
            _("pending_list", locale=random_locale).format(
                request_type=pending_message
            ),
        ]
    )
    kb = helper.extract_keyboard_entries(second_answer[1].reply_markup)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}: {duration}"


@pytest.mark.asyncio
async def test_poll_for_check_in_request(db_calls, routers, get_user):
    random_locale = helper.get_random_locale()
    test_function = routers.att_for_admin.poll_for_check_in_request
    action = Action.CHECK_IN
    pending_message = _("pending_attendance", locale=random_locale)
    button_name = _("CHECK_IN_button", locale=random_locale)

    user, membership = get_user(with_membership=True, locale=random_locale)
    polling_message = _("polling", locale=random_locale).format(
        request_type_string=pending_message,
        timeout_seconds=GlobalSettings().config.polling_timeout_seconds,
        button_name=button_name,
    )
    first_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in first_answer]) == sorted(
        [
            polling_message,
            _("polling_timeout", locale=random_locale).format(button_name=button_name),
        ]
    )
    db_calls.member.request_to_add_attendance(
        tg_id=user.tg_id, chat_id=CHAT.get("id"), mb_id=membership.id
    )
    second_answer = await helper.send_mocked_message_with_text_data_callback_admin(
        locale=random_locale, action=action, handler_to_mock=test_function
    )
    assert sorted([a.text for a in second_answer]) == sorted(
        [
            polling_message,
            _("pending_list", locale=random_locale).format(
                request_type=pending_message
            ),
        ]
    )
    kb = helper.extract_keyboard_entries(second_answer[1].reply_markup)
    assert len(kb) == 1
    assert kb[0] == f"{user.name}: {int(user.phone)}"


@pytest.mark.asyncio
async def test_locale_handler(routers):
    for loc in GlobalSettings().config.locales:
        answer = await helper.send_mocked_message_with_text_data_callback_non_admin(
            handler_to_mock=routers.misc.locale_handler,
            callback_data=loc,
        )
        answer_message = answer[0]
        assert answer_message.text == _("greeting", locale=loc).format(
            company_name=GlobalSettings().config.company_name
        )


@pytest.mark.asyncio
async def test_start_handler(routers):
    answer = await helper.send_mocked_message_with_text_data_message_non_admin(
        handler_to_mock=routers.misc.start_handler,
        message_text="start",
    )
    answer_message = answer[0]
    assert answer_message.text == "\n".join(
        [
            _("first_greeting", locale=locale)
            for locale in GlobalSettings().config.locales
        ]
    )
