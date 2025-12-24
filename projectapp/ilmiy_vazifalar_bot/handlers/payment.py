from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow
from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID
from projectapp.ilmiy_vazifalar_bot.handlers.first_channel import first_channel_kb

router = Router()


@router.message(OrderFlow.receipt, F.photo | F.document)
async def receipt_handler(msg: Message, state: FSMContext, bot):
    data = await state.get_data()

    if msg.photo:
        tg_file = msg.photo[-1]
        ext = "jpg"
    else:
        tg_file = msg.document
        ext = tg_file.file_name.split('.')[-1]

    file_id = tg_file.file_id

    file = await bot.get_file(file_id)
    downloaded = await bot.download_file(file.file_path)
    file_bytes = downloaded.read()

    order = await sync_to_async(Order.objects.create)(
        fullname=data["fullname"],
        phone=data["phone"],
        service=data["service"],
        price=data["price"],
        subject=data["subject"],
        topic=data["topic"],
        user_telegram_id=str(msg.from_user.id),
        receipt_tg_file_id=file_id,
        status="PENDING"
    )

    await sync_to_async(order.receipt_file.save)(
        f"receipt_{order.id}.{ext}",
        ContentFile(file_bytes)
    )

    caption = (
        f"🆕 <b>Yangi buyurtma</b>\n\n"
        f"🆔 ID: {order.id}\n"
        f"👤 {order.fullname}\n"
        f"📞 {order.phone}\n"
        f"📘 {order.service}\n"
        f"📚 {order.subject}\n"
        f"📝 {order.topic}\n"
        f"💰 {order.price}"
    )

    if msg.photo:
        await bot.send_photo(
            FIRST_CHANNEL_ID,
            file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=first_channel_kb(order.id)
        )
    else:
        await bot.send_document(
            FIRST_CHANNEL_ID,
            file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=first_channel_kb(order.id)
        )

    await msg.answer("✅ Chek qabul qilindi.")
    await state.clear()
