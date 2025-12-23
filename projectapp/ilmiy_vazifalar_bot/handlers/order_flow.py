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

    # 1️⃣ Faylni aniqlash
    if msg.photo:
        tg_file = msg.photo[-1]
        ext = "jpg"
        file_type = "photo"
    else:
        tg_file = msg.document
        ext = tg_file.file_name.split(".")[-1]
        file_type = "document"

    tg_file_id = tg_file.file_id

    # 2️⃣ Telegramdan yuklab olish
    file_info = await bot.get_file(tg_file_id)
    downloaded = await bot.download_file(file_info.file_path)
    file_bytes = downloaded.read()

    # 3️⃣ Order yaratish
    order = await sync_to_async(Order.objects.create)(
        fullname=data["fullname"],
        phone=data["phone"],
        service=data["service"],
        price=data["price"],
        subject=data["subject"],
        topic=data["topic"],
        user_telegram_id=str(msg.from_user.id),
        receipt_tg_file_id=tg_file_id,
        status="PENDING"
    )

    # 4️⃣ Chekni serverga saqlash
    await sync_to_async(order.receipt_file.save)(
        f"receipt_{order.id}.{ext}",
        ContentFile(file_bytes)
    )

    # 5️⃣ First channel caption
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

    # 6️⃣ First channelga YUBORISH (TO‘G‘RI)
    if file_type == "photo":
        await bot.send_photo(
            chat_id=FIRST_CHANNEL_ID,
            photo=tg_file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=first_channel_kb(order.id)
        )
    else:
        await bot.send_document(
            chat_id=FIRST_CHANNEL_ID,
            document=tg_file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=first_channel_kb(order.id)
        )

    await msg.answer("✅ Chek qabul qilindi. Tekshirilmoqda...")
    await state.clear()
