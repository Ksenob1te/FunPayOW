from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import environments
from .handlers import *

bot: Bot = Bot(token=environments.telegram.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp: Dispatcher = Dispatcher()

dp.include_router(cancel_router)
dp.include_router(add_router)
dp.include_router(check_router)
dp.include_router(remove_router)
dp.include_router(start_router)
dp.include_router(unresolved_router)
dp.include_router(static_router)
dp.include_router(all_codes_router)
dp.include_router(payment_router)