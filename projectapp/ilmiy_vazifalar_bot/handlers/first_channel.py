from aiogram import Router, F
from aiogram.types import CallbackQuery
from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.config import SECOND_CHANNEL_ID

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    order = Order.objects.get(id=order_id)
    order.status = "payment_approved"
    order.approved_by = call.from_user.full_name
    order.save()

    await call.bot.send_message(order.user_telegram_id, "✅ To‘lov tasdiqlandi!")
    # Endi order second channel ga o'tadi
    await call.bot.send_message(SECOND_CHANNEL_ID, f"Yangi buyurtma: {order.fullname}, {order.service_type}")
