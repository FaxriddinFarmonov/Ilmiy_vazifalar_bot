from aiogram import Router
from aiogram.types import Message
from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID
from projectapp.models import Order

router = Router()

async def send_to_first_channel(bot, order: Order):
    text = f"""
🆕 YANGI TO‘LOV

👤 {order.fullname}
📚 {order.service_type}
💰 {order.price} so‘m

Tasdiqlaysizmi?
"""
    # Inline tugmalar bilan tasdiqlash mumkin (ha/yo'q)
    await bot.send_message(FIRST_CHANNEL_ID, text)
