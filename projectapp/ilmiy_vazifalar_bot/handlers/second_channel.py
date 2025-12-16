from aiogram import Router, F
from aiogram.types import CallbackQuery
from projectapp.models import Order

router = Router()

@router.callback_query(F.data.startswith("take_"))
async def take_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    order = Order.objects.get(id=order_id)
    order.status = "taken"
    order.taken_by = call.from_user.full_name
    order.save()

    await call.bot.send_message(order.user_telegram_id, "📌 Buyurtmangiz qabul qilindi. Tez orada tayyor bo‘ladi.")

@router.callback_query(F.data.startswith("ready_"))
async def ready_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    order = Order.objects.get(id=order_id)
    order.status = "ready"
    order.save()

    await call.bot.send_document(order.user_telegram_id, document=order.file_id, caption="✅ Buyurtmangiz tayyor!")
