import asyncio
import logging
from src.database import create_db_and_tables, sessionmanager, get_db_session
from src.telegram import bot, dp


async def main():
    await create_db_and_tables()
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logging.info("Starting bot")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
        if sessionmanager._engine is not None:
            asyncio.run(sessionmanager.close())