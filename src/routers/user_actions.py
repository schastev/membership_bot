import logging

from aiogram import Router

from src.utils import user_actions as user_action_utils

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, Message

user_actions = Router()


class RegistrationStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


class UserUpdateStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


@user_actions.message(Command("register"))
@user_actions.message(F.text.casefold() == "register")
async def register_handler(message: Message, state: FSMContext):
    if not user_action_utils.check_user_registration_state(tg_id=message.from_user.id):
        await state.set_state(RegistrationStates.GET_NAME)
        await message.answer(
            "Welcome! Please enter your name.",
            reply_markup=ReplyKeyboardRemove()),
    else:
        await message.answer("You are already registered! You can go on to the membership management.")


@user_actions.message(Command("cancel"))
@user_actions.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.", reply_markup=ReplyKeyboardRemove(),
    )


@user_actions.message(RegistrationStates.GET_NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.GET_PHONE)
    await message.answer("Please enter your phone number.")


@user_actions.message(RegistrationStates.GET_PHONE)
async def process_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    name = data.get('name')
    phone = data.get('phone')
    await state.clear()
    await message.answer(f"Thank you for registering! Your name is {name} and your phone number is {phone}.")
    user_action_utils.register_user(name=name, phone=phone, tg_id=message.from_user.id)
    

@user_actions.message(Command("change name"))
@user_actions.message(F.text.casefold() == "change name")
async def change_name_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_NAME)
    await message.answer("Please enter your new name.", reply_markup=ReplyKeyboardRemove())


@user_actions.message(Command("change phone"))
@user_actions.message(F.text.casefold() == "change phone")
async def change_phone_handler(message: Message, state: FSMContext):
    await state.set_state(UserUpdateStates.GET_PHONE)
    await message.answer("Please enter your new phone.", reply_markup=ReplyKeyboardRemove())


@user_actions.message(UserUpdateStates.GET_NAME)
async def process_change_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await state.clear()
    await message.answer("Your name has been updated.")
    name = data.get('name')
    user_action_utils.update_name(new_name=name, tg_id=message.from_user.id)


@user_actions.message(UserUpdateStates.GET_PHONE)
async def process_change_phone(message: Message, state: FSMContext):
    data = await state.update_data(phone=message.text)
    await state.clear()
    await message.answer("Your phone has been updated.")
    phone = data.get("phone")
    user_action_utils.update_phone(new_phone=phone, tg_id=message.from_user.id)
    