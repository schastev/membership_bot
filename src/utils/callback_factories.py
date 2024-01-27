from aiogram.filters.callback_data import CallbackData


class MembershipRequestCallbackFactory(CallbackData, prefix="mb_request_value"):
    member_tg_id: int
    member_name: str
    value: int = 0
    chat_id: int
    id: int
