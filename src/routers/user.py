import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery

import translation
from src.routers.mb_for_admin import main_buttons
from src.utils import db_user as user_action_utils

router = Router()
_ = translation.i18n.gettext


class RegistrationStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


class UserUpdateStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


@router.callback_query(F.data == "button_register")
async def register_handler(callback: CallbackQuery, state: FSMContext):
    if not user_action_utils.check_user_registration_state(tg_id=callback.from_user.id):
        await state.set_state(RegistrationStates.GET_NAME)
        await callback.message.answer(text=_("welcome"), reply_markup=ReplyKeyboardRemove()),
    else:
        await callback.message.answer(
            text=_("already_registered"), reply_markup=main_buttons(user_id=callback.from_user.id)
        )
    await callback.answer()


@router.callback_query(F.data == "button_cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(_("cancelled_state_log").format(current_state))
    await state.set_state(None)
    await callback.message.answer(_("cancelled"), reply_markup=main_buttons(user_id=callback.from_user.id))
    await callback.answer()


@router.message(RegistrationStates.GET_NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.GET_PHONE)
    await message.answer(_("enter_info").format("", _("phone")).replace("  ", " "))


@router.message(RegistrationStates.GET_PHONE)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    phone = message.text
    data.pop("name")
    await state.update_data(name=None)
    await state.set_state(None)
    lang = data.get("locale")
    added_user = user_action_utils.register_user(name=name, phone=phone, tg_id=message.from_user.id, language=lang)
    await message.answer(
        _("successful_registration").format(added_user.name, int(added_user.phone)),
        reply_markup=main_buttons(user_id=message.from_user.id), resize_keyboard=True
    )


@router.callback_query(F.data == "button_change_name")
async def change_name_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_NAME)
    await callback.message.answer(_("enter_info").format(_("new"), _("name")), reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@router.callback_query(F.data == "button_change_phone")
async def change_phone_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_PHONE)
    await callback.message.answer(_("enter_info").format(_("new"), _("phone")), reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@router.message(UserUpdateStates.GET_NAME)
async def process_change_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await state.set_state(None)
    name = data.get("name")
    updated_user = user_action_utils.update_name(new_name=name, tg_id=message.from_user.id)
    await message.answer(
        _("updated_info").format(updated_user.name, _("name")),
        reply_markup=main_buttons(user_id=message.from_user.id)
    )


@router.message(UserUpdateStates.GET_PHONE)
async def process_change_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    await state.set_state(None)
    phone = int(data.get("phone"))
    updated_user = user_action_utils.update_phone(new_phone=phone, tg_id=message.from_user.id)
    await message.answer(
        _("updated_info").format(updated_user.name, _("phone")),
        reply_markup=main_buttons(user_id=message.from_user.id),
    )
