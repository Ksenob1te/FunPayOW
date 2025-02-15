from src.database import sessionmanager
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import CodesRepository, Codes, UserRepository, User

from typing import List, Dict
import logging


class CodeService:
    # codes_field: List[Codes] = None

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.codes_repository = CodesRepository(session)
        self.logger = logging.getLogger(__name__)

    async def get_by_code(self, code: str) -> Codes:
        return await self.codes_repository.get_by_code(code)

    async def get_unresolved_codes(self) -> List[Codes]:
        return await self.codes_repository.get_unresolved()

    async def get_unresolved_codes_str(self) -> str:
        codes = await self.get_unresolved_codes()
        if len(codes) == 0:
            return "There are no unresolved codes"
        resulted_text = "Unresolved codes:\n"
        for i, code in enumerate(codes):
            resulted_text += f"{i + 1}. Code: <code>{code.code}</code>\n"
        return resulted_text

    async def get_codes(self, user_field: User) -> List[Codes]:
        return await self.codes_repository.get_by_user(user_field.id)

    async def get_codes_str(self, user_field: User, admin: bool = False) -> str:
        codes = await self.get_codes(user_field)
        if len(codes) == 0:
            return "You don't have any codes"
        if not admin:
            resulted_text = "Your codes are:\n"
        else:
            resulted_text = ""
        codes_sold: List[str] = []
        codes_selling: List[str] = []
        codes_pending: List[str] = []
        for i, code in enumerate(codes):
            code_text = f"<code>{(code.code[:9] + "..." if not admin else code.code)}</code>"
            if code.status == "resolved":
                codes_selling.append(f"💵 Code ({code_text}) on sale\n")
            elif code.status == "sold":
                codes_sold.append(f"✅ Code ({code_text}) sold\n")
            elif code.status == "unresolved":
                codes_pending.append(f"⏸ Code ({code_text}) is pending\n")

        index = max(len(codes_sold) - 4, 1)
        for code in codes_sold[-5:]:
            resulted_text += f"{index}. {code}"
            index += 1

        for code in codes_selling:
            resulted_text += f"{index}. {code}"
            index += 1

        for code in codes_pending:
            resulted_text += f"{index}. {code}"
            index += 1

        if not admin:
            resulted_text += (f"\nYour balance is {user_field.balance}\n\nYou have sold {len(codes_sold)} codes,"
                              f" now selling {len(codes_selling)} codes, {len(codes_pending)} pending")
        return resulted_text

    async def get_all_codes(self) -> List[Codes]:
        return await self.codes_repository.get_all()

    async def get_all_codes_str(self) -> str:
        codes = await self.get_all_codes()
        if len(codes) == 0:
            return "There are no codes"
        resulted_text = ""
        user_fields: List[User] = await self.user_repository.get_all()
        for user_field in user_fields:
            resulted_text += f"User: <b>{await self.user_repository.get_full_name(user_field)} ({user_field.username})</b>\n"
            resulted_text += f"Balance: <b>{user_field.balance}</b>\n"
            resulted_text += await self.get_codes_str(user_field, admin=True)
            resulted_text += "\n\n"
        return resulted_text

    async def add_code(self, user_field: User, code: str) -> Codes:
        if await self.codes_repository.get_by_code(code) is not None:
            raise Exception("Code already exists")
        code_field = await self.codes_repository.create(code=code, user_id=user_field.id)
        return code_field

    async def remove_code(self, code: str):
        code_field = await self.codes_repository.get_by_code(code)
        if code_field is None:
            raise Exception("Code not found")
        if code_field.status != "unresolved":
            raise Exception("Code is not unresolved")
        await self.codes_repository.remove(code_field)
        return code_field


    async def update_codes(self, codes_onsale: List[str], price: int):
        all_codes = await self.codes_repository.get_all()
        for code in all_codes:
            if code.status == "resolved" and code.code not in codes_onsale:
                code.status = "sold"
                await self.user_repository.add_balance(code.user, price)
            elif code.status == "unresolved" and code.code in codes_onsale:
                code.status = "resolved"
            await self.session.commit()
        return True


