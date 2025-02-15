from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from src.database import sessionmanager
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..callback import *
from ..service import UserService

start_router: Router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message):
    async with sessionmanager.session() as session:
        user_service: UserService = UserService(message, session)
        await user_service.init_user()
        start_text = "Select an action:"

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="[+] Add code", callback_data=AddCodeCallback().pack())
        keyboard.button(text="[!] My codes", callback_data=CheckCodeCallback().pack())
        await message.reply(start_text, reply_markup=keyboard.as_markup())
        await session.commit()