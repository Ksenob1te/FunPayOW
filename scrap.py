from src.scrap.account import Account
from src.database import sessionmanager
from src.telegram.service import StaticService, CodeService
import logging
import asyncio


async def get_info():
    async with sessionmanager.session() as session:
        static_service: StaticService = StaticService(session)
        golden_key = await static_service.get_value_by_code("golden_key")
        user_agent = await static_service.get_value_by_code("user_agent")
        account = Account(
            golden_key=golden_key,
            user_agent=user_agent,
            requests_timeout=10
        ).get()

        lot_id = int(await static_service.get_value_by_code("lot_id"))
        lot_fields = account.get_lot_fields(lot_id)

        code_service: CodeService = CodeService(session)
        await code_service.update_codes(lot_fields.get_products(), int(lot_fields.price))


if __name__ == "__main__":
    logging.info("Scrap update")
    asyncio.run(get_info())