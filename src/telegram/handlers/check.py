from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.database import sessionmanager
from ..callback import *
from ..service import UserService, CodeService

check_router: Router = Router()


@check_router.message(Command("check"))
@check_router.callback_query(CheckCodeCallback.filter())
async def command_check(call: CallbackQuery | Message):
    if isinstance(call, CallbackQuery):
        message = call.message
    else:
        message = call

    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        code_service: CodeService = CodeService(session)
        user_field = await user_service.get_user()
        codes_str = await code_service.get_codes_str(user_field)
        await message.answer(codes_str)
        await session.commit()

    if isinstance(call, CallbackQuery):
        await call.answer()