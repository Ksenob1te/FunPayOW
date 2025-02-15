from src.database import sessionmanager
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import UserRepository, User

from src.telegram.exceptions import (
    UserNotFoundException
    )

import logging

class UserService:
    user_field: User = None

    def __init__(self, message: Message, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.logger = logging.getLogger(__name__)
        self.message = message

    async def init_user(self):
        self.user_field = await self.user_repository.get_by_chat_id(str(self.message.chat.id))
        if self.user_field is not None:
            return
        username = None
        if self.message.chat.username is not None:
            username = self.message.chat.username
        elif self.message.chat.title is not None:
            username = self.message.chat.title
        self.user_field = await self.user_repository.create(
            chat_id=str(self.message.chat.id),
            username=username,
            first_name=self.message.chat.first_name,
            last_name=self.message.chat.last_name
        )
        self.logger.info(f"User {self.user_field} created")
        await self.session.commit()
        if self.user_field is None:
            self.logger.error(f"Error while creating user {self.message.chat.id}")
            raise UserNotFoundException

    async def get_user(self) -> User:
        if self.user_field is None:
            await self.init_user()
        return self.user_field

    async def check_admin(self) -> bool:
        if self.user_field is None:
            await self.init_user()
        return bool(self.user_field.is_admin)

    async def get_admins_ids(self) -> list:
        admins = await self.user_repository.get_admins()
        return [admin.chat_id for admin in admins]

    async def get_full_name(self, user: User) -> str:
        return await self.user_repository.get_full_name(user)

