from src.database import sessionmanager
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Static, StaticRepository

from typing import List
import logging


class StaticService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = StaticRepository(session)

    async def get_by_code(self, code: str) -> Static | None:
        return await self.repository.get_by_code(code)

    async def get_value_by_code(self, code: str) -> str | None:
        static_value = await self.repository.get_by_code(code)
        if static_value:
            return static_value.value
        return None

    async def get_all_codes(self) -> List[str]:
        return await self.repository.get_all_codes()

    async def set_or_create(self, code: str, value: str) -> Static:
        return await self.repository.set_or_create(code, value)
