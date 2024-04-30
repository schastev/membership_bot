import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config_reader import config
from src.routers.user import _
from src.utils import translation
from src.utils.constants import Action, Modifier
from src.utils.menu import main_buttons, UserState

router = Router()
_ = translation.i18n.gettext


async def greeting(message: Message, user_id: int, user_state: UserState | None = None):
    await message.answer(
        text=_("greeting").format(company_name=config.company_name),
        reply_markup=main_buttons(user_id=user_id, user_state=user_state)
    )


@router.callback_query(F.data == f"{Action.CANCEL}{Modifier.CALLBACK}")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(_("cancelled_state_log").format(current_state=current_state))
    await callback.message.answer(_("cancelled"), reply_markup=main_buttons(user_id=callback.from_user.id))
    await state.set_state(None)
    await callback.answer()


@router.message(F.text)
async def gotta_catch_them_all(message: Message):
    print(message.text)


@router.callback_query(F.data)
async def gotta_catch_all_of_them(callback: CallbackQuery):
    print(callback.data)
