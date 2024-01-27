from aiogram.filters.callback_data import CallbackData


class MembershipRequestCallbackFactory(CallbackData, prefix="mb_request"):
    member_tg_id: int
    member_name: str
    value: int = 0
    chat_id: int
    id: int


class MBRequestListCallbackFactory(MembershipRequestCallbackFactory, prefix="mb_request_list"):
    pass


class MBRequestValueCallbackFactory(MembershipRequestCallbackFactory, prefix="mb_request_value"):
    pass
