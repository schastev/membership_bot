from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import config_reader
from src.routers.mb_for_admin import main_buttons
from src.utils import bot_helpers, translation
from src.db_calls import user as user_action_utils
from src.utils.constants import Action, Modifier
from src.utils.menu import locale_buttons, user_settings_options

router = Router()
_ = translation.i18n.gettext


class RegistrationStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


class UserUpdateStates(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()


@router.callback_query(F.data == f"{Action.REGISTER}{Modifier.CALLBACK}")
async def register_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not user_action_utils.check_user_registration_state(tg_id=callback.from_user.id):
        await state.set_state(RegistrationStates.GET_NAME)
        await callback.message.answer(text=_("welcome")),
    else:
        await callback.message.answer(
            text=_("REGISTER_error_already_registered"), reply_markup=main_buttons(user_id=callback.from_user.id)
        )
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(F.data == f"{Action.CHANGE_SETTINGS}{Modifier.CALLBACK}")
async def change_user_settings(callback: CallbackQuery):
    await callback.message.answer(text=_("CHANGE_SETTINGS_text"), reply_markup=user_settings_options())
    await callback.answer()


@router.message(RegistrationStates.GET_NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.GET_PHONE)
    await message.answer(_("CHANGE_SETTINGS_first_phone_query"))


@router.message(RegistrationStates.GET_PHONE)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(None)
    name = data.get("name")
    phone = message.text
    await state.update_data(name=None)
    locale = data.get("locale")
    added_user = user_action_utils.register_user(name=name, phone=phone, tg_id=message.from_user.id, locale=locale)
    await message.answer(
        _("REGISTER_ok").format(name=added_user.name, phone=int(added_user.phone)),
        reply_markup=main_buttons(user_id=message.from_user.id)
    )


@router.callback_query(F.data == f"{Action.CHANGE_NAME}{Modifier.CALLBACK}")
async def change_name_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(UserUpdateStates.GET_NAME)
    await callback.message.answer(_("CHANGE_SETTINGS_query_name"))
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.callback_query(F.data == f"{Action.CHANGE_PHONE}{Modifier.CALLBACK}")
async def change_phone_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(UserUpdateStates.GET_PHONE)
    await callback.message.answer(_("CHANGE_SETTINGS_query_phone"))
    await bot_helpers.rm_buttons_from_last_message(callback=callback, bot=bot)
    await callback.answer()


@router.message(UserUpdateStates.GET_NAME)
async def process_change_name(message: Message, state: FSMContext):
    name = message.text
    updated_user = user_action_utils.update_name(new_name=name, tg_id=message.from_user.id)
    await message.answer(
        _("CHANGE_SETTINGS_name_ok").format(name=updated_user.name),
        reply_markup=main_buttons(user_id=message.from_user.id)
    )
    await state.set_state(None)


@router.message(UserUpdateStates.GET_PHONE)
async def process_change_phone(message: Message, state: FSMContext):
    phone = int(message.text)
    updated_user = user_action_utils.update_phone(new_phone=phone, tg_id=message.from_user.id)
    await message.answer(
        _("CHANGE_SETTINGS_phone_ok").format(name=updated_user.name),
        reply_markup=main_buttons(user_id=message.from_user.id),
    )
    await state.set_state(None)


@router.callback_query(F.data == f"{Action.CHANGE_LOCALE}{Modifier.CALLBACK}")
async def change_locale_handler(callback: CallbackQuery):
    menu_buttons = locale_buttons()
    greetings = [_("CHANGE_LOCALE_text", locale=locale) for locale in config_reader.config.locales]
    await callback.message.answer("\n".join(greetings), reply_markup=menu_buttons)
    await callback.answer()
