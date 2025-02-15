from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.database import sessionmanager
from ..service import UserService, CodeService


unresolved_router: Router = Router()

@unresolved_router.message(Command("unresolved"))
async def command_unresolved(message: Message):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        if not await user_service.check_admin():
            await message.answer("You are not an admin")
            return
        code_service: CodeService = CodeService(session)
        codes_text = await code_service.get_unresolved_codes_str()
        await message.answer(codes_text)
        await session.commit()