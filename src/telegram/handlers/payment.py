from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.database import sessionmanager
from ..service import StaticService, UserService
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..callback import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

payment_router: Router = Router()


class PaymentStates(StatesGroup):
    make_payment = State()


@payment_router.message(Command("payment"))
async def command_payment(message: Message, ):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        start_text = "Select user to make payment to"

        keyboard = InlineKeyboardBuilder()
        for user_field in await user_service.get_all():
            user_field_name = await user_service.get_name(user_field)
            keyboard.button(text=user_field_name, callback_data=PaymentCallback(user_id=user_field.id).pack())
        keyboard.button(text="Cancel", callback_data=CancelCallback().pack())
        keyboard.adjust(1, repeat=True)
        await message.answer(start_text, reply_markup=keyboard.as_markup())


@payment_router.callback_query(PaymentCallback.filter())
async def select_payment(call: CallbackQuery, callback_data: PaymentCallback, state: FSMContext):
    user_id = callback_data.user_id
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(call.message, session)
        if not await user_service.check_admin():
            await call.answer("You are not an admin")
            return
        user_field = await user_service.get_from_id(user_id)
        builder = InlineKeyboardBuilder()
        builder.button(text="Cancel", callback_data=CancelCallback().pack())
        new_message = await call.message.answer(
            f'Provide me amount for payment for user: "{await user_service.get_name(user_field)}".\n\n'
            f'Current value: {await user_service.get_balance(user_field)}',
            reply_markup=builder.as_markup(),
        )
        await state.set_state(PaymentStates.make_payment)
        await state.set_data({"message_id": new_message.message_id, "user_id": user_id})
        await call.answer()


@payment_router.message(PaymentStates.make_payment)
async def payment_final(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data["user_id"]
    prev_message_id = data["message_id"]
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        if not await user_service.check_admin():
            await message.reply("You are not an admin")
            return
        user_field = await user_service.get_from_id(user_id)
        try:
            await user_service.make_payment(user_field, int(message.text))
            await message.reply(
                f'Balance changed for user: "{await user_service.get_name(user_field)}".\n\n'
                f'Current value: {await user_service.get_balance(user_field)}'
            )
            await session.commit()
        except Exception as e:
            await message.reply(
                f'Failed to change value\nError: {e}',
            )

    await message.bot.delete_message(chat_id=message.chat.id, message_id=prev_message_id)
    await state.clear()
