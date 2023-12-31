import logging

from aiogram import Router, F

from src.utils import user as user_action_utils

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, Message, ReplyKeyboardMarkup
from config_reader import config
from src.utils.menu import main_buttons

router = Router()
locale = config


class RegistrationStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


class UserUpdateStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


@router.message(Command(locale.register_button))
@router.message(F.text.casefold() == locale.register_button.casefold())
async def register_handler(message: Message, state: FSMContext):
    if not user_action_utils.check_user_registration_state(tg_id=message.from_user.id):
        await state.set_state(RegistrationStates.GET_NAME)
        await message.answer(text=locale.welcome, reply_markup=ReplyKeyboardRemove()),
    else:
        await message.answer(text=locale.already_registered)


@router.message(Command(locale.cancel))
@router.message(F.text.casefold() == locale.cancel.casefold())
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info(locale.cancelled_state_log.format(current_state))
    await state.clear()
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        locale.cancelled, reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(RegistrationStates.GET_NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.GET_PHONE)
    await message.answer(locale.enter_info.format("", locale.phone).replace("  ", " "))


@router.message(RegistrationStates.GET_PHONE)
async def process_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    name = data.get(locale.name)
    phone = data.get(locale.phone)
    await state.clear()
    added_user = user_action_utils.register_user(name=name, phone=phone, tg_id=message.from_user.id)
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        locale.successful_registration.format(added_user.name, int(added_user.phone)),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )
    

@router.message(Command(locale.change_name_button))
@router.message(F.text.casefold() == locale.change_name_button.casefold())
async def change_name_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_NAME)
    await message.answer(locale.enter_info.format(locale.new, locale.name), reply_markup=ReplyKeyboardRemove())


@router.message(Command(locale.change_phone_button))
@router.message(F.text.casefold() == locale.change_phone_button.casefold())
async def change_phone_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_PHONE)
    await message.answer(locale.enter_info.format(locale.new, locale.phone), reply_markup=ReplyKeyboardRemove())


@router.message(UserUpdateStates.GET_NAME)
async def process_change_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await state.clear()
    name = data.get(locale.name)
    updated_user = user_action_utils.update_name(new_name=name, tg_id=message.from_user.id)
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        locale.updated_info.format(updated_user.name, locale.name),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )


@router.message(UserUpdateStates.GET_PHONE)
async def process_change_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    await state.clear()
    phone = int(data.get(locale.phone))
    updated_user = user_action_utils.update_phone(new_phone=phone, tg_id=message.from_user.id)
    menu_buttons = main_buttons(message.from_user.id)
    await message.answer(
        locale.updated_info.format(updated_user.name, locale.phone),
        reply_markup=ReplyKeyboardMarkup(keyboard=[menu_buttons], resize_keyboard=True)
    )
    