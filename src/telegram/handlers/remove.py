from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.database import sessionmanager
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..callback import *
from ..service import UserService, CodeService
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

remove_router: Router = Router()

class RemoveCodeStates(StatesGroup):
    remove = State()


@remove_router.message(Command("remove"))
async def command_remove(message: Message, state: FSMContext):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        if not await user_service.check_admin():
            await message.answer("You are not an admin")
            return
        codes_text = "Type in code to remove"
        builder = InlineKeyboardBuilder()
        builder.button(text="Cancel", callback_data=CancelCallback().pack())
        new_message = await message.answer(codes_text, reply_markup=builder.as_markup())

        await state.set_state(RemoveCodeStates.remove)
        await state.set_data({"message_id": new_message.message_id})


@remove_router.message(RemoveCodeStates.remove)
async def remove_code(message: Message, state: FSMContext):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        code_service: CodeService = CodeService(session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        try:
            await code_service.remove_code(message.text)
        except Exception as e:
            await message.reply(f"Failed to remove code {message.text}.\nError: {e}")
        else:
            await session.commit()
            await message.reply(f"Code {message.text} removed")

    data = await state.get_data()
    prev_message_id = data["message_id"]
    await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    await state.clear()