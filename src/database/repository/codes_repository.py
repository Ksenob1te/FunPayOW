from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Codes
from uuid import UUID
from typing import List
import logging


class CodesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, code_id: UUID) -> Codes | None:
        stmt = select(Codes).where(Codes.id == code_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_code(self, code: str) -> Codes | None:
        stmt = select(Codes).where(Codes.code == code).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_user(self, user_id: UUID) -> List[Codes] | None:
        stmt = select(Codes).where(Codes.user_id == user_id).order_by(Codes.created_at)
        return list(await self.session.scalars(stmt))

    async def get_unresolved(self) -> List[Codes] | None:
        stmt = select(Codes).where(Codes.status == "unresolved").order_by(Codes.created_at)
        return list(await self.session.scalars(stmt))

    async def get_all(self) -> List[Codes] | None:
        stmt = select(Codes).order_by(Codes.created_at)
        return list(await self.session.scalars(stmt))

    async def create(self, code: str, user_id: UUID, status: str = "unresolved") -> Codes:
        code = Codes(code=code,
                    user_id=user_id,
                    status=status
                     )
        self.session.add(code)
        await self.session.flush()
        self.logger.info(f"User {code.id} created (user_id: {user_id}), id: {code.id}")
        return await self.get_by_id(code.id)

    async def remove(self, code: Codes):
        await self.session.delete(code)
        await self.session.flush()
        self.logger.info(f"Code {code.id} removed")
        return True
