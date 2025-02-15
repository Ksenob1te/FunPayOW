from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.database import sessionmanager
from ..service import StaticService, UserService
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..callback import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


static_router: Router = Router()


class StaticStates(StatesGroup):
    change_static = State()
    add_static = State()


@static_router.message(Command("static"))
async def command_start(message: Message, ):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        static_service: StaticService = StaticService(session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        start_text = "Select value to change"

        keyboard = InlineKeyboardBuilder()
        for code in await static_service.get_all_codes():
            keyboard.button(text=code, callback_data=StaticCallback(static_code=code).pack())
        keyboard.button(text="[+] Add New", callback_data=AddStaticCallback().pack())
        keyboard.adjust(2, repeat=True)
        await message.answer(start_text, reply_markup=keyboard.as_markup())



@static_router.callback_query(StaticCallback.filter())
async def change_static(call: CallbackQuery, callback_data: StaticCallback, state: FSMContext):
    static_code = callback_data.static_code
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(call.message, session)
        static_service: StaticService = StaticService(session)
        if not await user_service.check_admin():
            await call.answer("You are not an admin")
            return
        builder = InlineKeyboardBuilder()
        builder.button(text="Cancel", callback_data=CancelCallback().pack())
        new_message = await call.message.answer(
            f'Provide me a new value for "{static_code}".\n\n'
            f'Current value: {await static_service.get_value_by_code(static_code)}',
            reply_markup=builder.as_markup(),
        )
        await state.set_state(StaticStates.change_static)
        await state.set_data({"message_id": new_message.message_id, "static_code": static_code})
        await call.answer()


@static_router.message(StaticStates.change_static)
async def assert_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    static_code = data["static_code"]
    prev_message_id = data["message_id"]
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        static_service: StaticService = StaticService(session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        try:
            await static_service.set_or_create(static_code, message.text)
            await session.commit()
        except Exception as e:
            await message.reply(
                f'Failed to change value\nError: {e}',
            )
        else:
            await message.reply(
                f'Changed value for "{static_code}" to "{message.text}".',
            )

    await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    await state.clear()


@static_router.callback_query(AddStaticCallback.filter())
async def add_static(call: CallbackQuery, state: FSMContext):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(call.message, session)
        if not await user_service.check_admin():
            await call.answer("You are not an admin")
            return
        builder = InlineKeyboardBuilder()
        builder.button(text="Cancel", callback_data=CancelCallback().pack())
        new_message = await call.message.answer(
            f'Provide me a new static code.',
            reply_markup=builder.as_markup(),
        )
        await state.set_state(StaticStates.add_static)
        await state.set_data({"message_id": new_message.message_id})
        await call.answer()


@static_router.message(StaticStates.add_static)
async def add_static_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_message_id = data["message_id"]
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        static_service: StaticService = StaticService(session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        try:
            await static_service.set_or_create(message.text, "")
            await session.commit()
        except Exception as e:
            await message.reply(
                f'Failed to add static code.\nError: {e}',
            )
        else:
            await message.reply(
                f'Added static code "{message.text}".',
            )

    await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    await state.clear()
