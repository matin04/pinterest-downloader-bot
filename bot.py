import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, download, admin
from database.db import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    logging.info("Базаи маълумот бо муваффақият омода шуд.")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(download.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    from database.db import init_db
    asyncio.run(main())