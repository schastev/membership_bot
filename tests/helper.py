from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram_tests import MockedRequester
from aiogram_tests.handler import CallbackQueryHandler, MessageHandler
from aiogram_tests.types.dataset import CALLBACK_QUERY, USER, MESSAGE

from config_reader import GlobalSettings
from src.utils.constants import Modifier, Action


def extract_keyboard_entries(keyboard_markup: InlineKeyboardMarkup) -> List[str]:
    result = []
    [result.extend(r) for r in keyboard_markup.inline_keyboard]
    return [button.text.replace("_button", "") for button in result]


def get_random_locale() -> str:
    # return Random().choice(config_reader.config.locales)
    return "ru"  # todo fix en this working as ru


async def send_mocked_message_with_text_data_callback_non_admin(
    handler_to_mock, callback_data: str
):
    handler = CallbackQueryHandler(handler_to_mock)
    callback_query = CALLBACK_QUERY.as_object(
        data=callback_data,
        from_user=USER.as_object(id=GlobalSettings().config.admin_ids[0]),
    )
    call = await MockedRequester(handler).query(callback_query)
    answer = call.send_message.fetchall()
    return answer


async def send_mocked_message_with_text_data_callback_admin(
    locale: str, action: Action, handler_to_mock
):
    callback_data = f"{Modifier.ADMIN}{action}{Modifier.CALLBACK}"
    handler = CallbackQueryHandler(
        handler_to_mock,
        state_data={"locale": locale},
        dp_middlewares=[GlobalSettings().locale],
    )
    callback_query = CALLBACK_QUERY.as_object(
        data=callback_data,
        from_user=USER.as_object(id=GlobalSettings().config.admin_ids[0]),
    )
    call = await MockedRequester(handler).query(callback_query)
    answer = call.send_message.fetchall()
    return answer


async def send_mocked_message_with_factory_data_callback_admin(
    locale: str, handler_to_mock, factory: type(CallbackData), **factory_args
):
    handler = CallbackQueryHandler(
        handler_to_mock,
        factory.filter(),
        state_data={"locale": locale},
        dp_middlewares=[GlobalSettings().locale],
    )
    callback_query = CALLBACK_QUERY.as_object(
        data=factory(**factory_args).pack(),
        from_user=USER.as_object(id=GlobalSettings().config.admin_ids[0]),
    )
    call = await MockedRequester(handler).query(callback_query)
    answer = call.send_message.fetchall()
    return answer


async def send_mocked_message_with_text_data_message_non_admin(
    handler_to_mock, message_text: str
):
    handler = MessageHandler(handler_to_mock)
    message = MESSAGE.as_object(text=message_text)
    call = await MockedRequester(handler).query(message)
    answer = call.send_message.fetchall()
    return answer
