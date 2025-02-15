from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Static
from uuid import UUID
from typing import List
import logging


class StaticRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, code_id: UUID) -> Static | None:
        stmt = select(Static).where(Static.id == code_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_code(self, code: str) -> Static | None:
        stmt = select(Static).where(Static.code == code).limit(1)
        return await self.session.scalar(stmt)

    async def get_all_codes(self) -> List[str]:
        static_values = await self.session.scalars(select(Static))
        return [static.code for static in static_values]

    async def create(self, code: str, value: str) -> Static:
        code = Static(code=code,
                      value=value)
        self.session.add(code)
        await self.session.flush()
        self.logger.info(f"Code {code.id} created, id: {code.id}")
        return await self.get_by_id(code.id)

    async def set_or_create(self, code: str, value: str) -> Static:
        static_value = await self.get_by_code(code)
        if static_value:
            static_value.value = value
            await self.session.flush()
            return static_value
        return await self.create(code, value)
