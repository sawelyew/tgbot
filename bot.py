import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from data.dbservice import init_database
from handlers.start import start_router
from handlers.orders import order_router
from handlers.admin import admin_router

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(order_router)
    await init_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
