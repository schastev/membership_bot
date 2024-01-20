import logging
from gettext import gettext as _

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, Message

from config_reader import config
from translation import t
from src.utils import db_user as user_action_utils
from src.utils.misc import FullMenuMarkup

router = Router()
locale = config
_ = t.gettext


class RegistrationStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


class UserUpdateStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


@router.message(Command(_("register_button")))
@router.message(F.text.casefold() == _("register_button").casefold())
async def register_handler(message: Message, state: FSMContext):
    if not user_action_utils.check_user_registration_state(tg_id=message.from_user.id):
        await state.set_state(RegistrationStates.GET_NAME)
        await message.answer(text=_("welcome"), reply_markup=ReplyKeyboardRemove()),
    else:
        await message.answer(text=_("already_registered"))


@router.message(Command(_("cancel")))
@router.message(F.text.casefold() == _("cancel").casefold())
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(_("cancelled_state_log").format(current_state))
    await state.clear()
    await message.answer(
        _("cancelled"), reply_markup=FullMenuMarkup(user_id=message.from_user.id)
    )


@router.message(RegistrationStates.GET_NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.GET_PHONE)
    await message.answer(_("enter_info").format(_("phone")).replace("  ", " "))


@router.message(RegistrationStates.GET_PHONE)
async def process_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    name = data.get("name")
    phone = data.get("phone")
    await state.clear()
    added_user = user_action_utils.register_user(name=name, phone=phone, tg_id=message.from_user.id)
    await message.answer(
        _("successful_registration").format(added_user.name, int(added_user.phone)),
        reply_markup=FullMenuMarkup(user_id=message.from_user.id)
    )


@router.message(Command(_("change_name_button")))
@router.message(F.text.casefold() == _("change_name_button").casefold())
async def change_name_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_NAME)
    await message.answer(_("enter_info").format(_("new"), _("name")), reply_markup=ReplyKeyboardRemove())


@router.message(Command(_("change_phone_button")))
@router.message(F.text.casefold() == _("change_phone_button").casefold())
async def change_phone_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_PHONE)
    await message.answer(_("enter_info").format(_("new"), _("phone")), reply_markup=ReplyKeyboardRemove())


@router.message(UserUpdateStates.GET_NAME)
async def process_change_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await state.clear()
    name = data.get(_("name"))
    updated_user = user_action_utils.update_name(new_name=name, tg_id=message.from_user.id)
    await message.answer(
        _("updated_info").format(updated_user.name, _("name")),
        reply_markup=FullMenuMarkup(user_id=message.from_user.id)
    )


@router.message(UserUpdateStates.GET_PHONE)
async def process_change_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    await state.clear()
    phone = int(data.get(_("phone")))
    updated_user = user_action_utils.update_phone(new_phone=phone, tg_id=message.from_user.id)
    await message.answer(
        _("updated_info").format(updated_user.name, _("phone")),
        reply_markup=FullMenuMarkup(user_id=message.from_user.id)
    )
    