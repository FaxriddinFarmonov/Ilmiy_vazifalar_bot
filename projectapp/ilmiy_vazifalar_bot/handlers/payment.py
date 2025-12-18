from aiogram import Router, F
from aiogram.types import Message
from asgiref.sync import sync_to_async

from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID
from projectapp.ilmiy_vazifalar_bot.handlers.first_channel import first_channel_kb

router = Router()

@router.message(F.photo | F.document)
async def get_receipt(msg: Message, bot):
    if not msg.caption or not msg.caption.startswith("order:"):
        await msg.answer("❌ Caption yozing: order:ID (masalan: order:12)")
        return

    try:
        order_id = int(msg.caption.split(":")[1])
    except ValueError:
        await msg.answer("❌ Noto‘g‘ri format")
        return

    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        await msg.answer("❌ Buyurtma topilmadi")
        return

    # 📎 file aniqlash
    if msg.photo:
        file_id = msg.photo[-1].file_id
        send_func = bot.send_photo
    else:
        file_id = msg.document.file_id
        send_func = bot.send_document

    order.receipt_file_id = file_id
    order.status = "PENDING"
    await sync_to_async(order.save)()

    caption = (
        f"🆕 <b>Yangi to‘lov</b>\n\n"
        f"🆔 ID: {order.id}\n"
        f"👤 {order.fullname}\n"
        f"📘 {order.service}\n"
        f"💰 {order.price}\n\n"
        f"⏳ Tekshirilmoqda"
    )

    await send_func(
        FIRST_CHANNEL_ID,
        file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=first_channel_kb(order.id)
    )

    await msg.answer("✅ Chek adminga yuborildi")
