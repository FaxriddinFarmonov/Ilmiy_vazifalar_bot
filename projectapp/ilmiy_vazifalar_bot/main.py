import os
import django
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.handlers import start, order_flow, payment, first_channel, second_channel
from projectapp.ilmiy_vazifalar_bot.config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(order_flow.router)
    dp.include_router(payment.router)
    dp.include_router(first_channel.router)
    dp.include_router(second_channel.router)

    print("🤖 Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
