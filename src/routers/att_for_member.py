from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config_reader import GlobalSettings
from src.model.request import RequestType
from src.db_calls import member as db_member
from src.routers import for_member
from src.routers.helpers import get_active_membership_or_go_home
from src.utils import bot_helpers
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons

router = Router()
_ = GlobalSettings().i18n.gettext


@router.callback_query(F.data == f"{Action.VIEW_ATTENDANCES}{Modifier.CALLBACK}")
async def view_attendances(callback: CallbackQuery, bot: Bot, state: FSMContext):
    attendance_list = db_member.view_attendances_for_active_membership(
        tg_id=callback.from_user.id
    )
    if len(attendance_list) == 0:
        text = _("CHECK_IN_none")
    else:
        data = await state.get_data()
        text = "\n".join(
            [att.print(locale=data.get("locale")) for att in attendance_list]
        )
    await callback.message.answer(
        text, reply_markup=main_buttons(user_id=callback.from_user.id)
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)


@router.callback_query(F.data == f"{Action.CHECK_IN}{Modifier.CALLBACK}")
async def request_to_add_attendance(callback: CallbackQuery, bot: Bot):
    await get_active_membership_or_go_home(callback=callback)
    await for_member.add_request(
        message=callback.message,
        tg_id=callback.from_user.id,
        request_type=RequestType.ATTENDANCE,
    )
    await callback.answer()
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
