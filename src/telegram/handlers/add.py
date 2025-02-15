from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.database import sessionmanager
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..callback import *
from ..service import UserService, CodeService
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

add_router: Router = Router()


class AddCodeStates(StatesGroup):
    add = State()


@add_router.message(Command("add"))
@add_router.callback_query(AddCodeCallback.filter())
async def command_add(call: CallbackQuery | Message, state: FSMContext):
    if isinstance(call, CallbackQuery):
        message = call.message
    else:
        message = call

    builder = InlineKeyboardBuilder()
    builder.button(text="Cancel", callback_data=CancelCallback().pack())
    new_message = await message.answer(
        f'Provide me a code.',
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AddCodeStates.add)
    await state.set_data({"message_id": new_message.message_id})

    if isinstance(call, CallbackQuery):
        await call.answer()


@add_router.message(AddCodeStates.add)
async def assert_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_message_id = data["message_id"]
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        code_service: CodeService = CodeService(session)
        user_field = await user_service.get_user()
        try:
            await code_service.add_code(user_field, message.text)
            await session.commit()
        except Exception as e:
            await message.reply(
                f'Failed to add code ("{message.text[:9]}...").\nError: {e}',
            )
        else:
            await message.reply(
                f'Added your code ("{message.text[:9]}...") to "pending" list.',
            )
            admins_ids = await user_service.get_admins_ids()
            name = await user_service.get_full_name(user_field)
            if name is None:
                name = user_field.username
            for admin_id in admins_ids:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=f'User <b>{name}</b> added code:\n<code>{message.text}</code>'
                )
    await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    await state.clear()