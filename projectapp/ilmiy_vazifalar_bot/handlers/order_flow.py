# from aiogram import Router, F
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from asgiref.sync import sync_to_async
#
# from projectapp.models import Order
# from projectapp.ilmiy_vazifalar_bot.states import OrderFlow
# from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID
#
# router = Router()
#
# def first_channel_kb(order_id: int):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="✅ To‘lovni tasdiqlash",
#                     callback_data=f"admin_accept:{order_id}"
#                 )
#             ]
#         ]
#     )
#
# @router.message(OrderFlow.receipt, F.photo | F.document)
# async def receipt(msg: Message, state: FSMContext, bot):
#     data = await state.get_data()
#
#     if msg.photo:
#         file_id = msg.photo[-1].file_id
#         send_func = bot.send_photo
#     else:
#         file_id = msg.document.file_id
#         send_func = bot.send_document
#
#     order = await sync_to_async(Order.objects.create)(
#         fullname=data["fullname"],
#         phone=data["phone"],
#         service=data["service"],
#         price=data["price"],
#         subject=data["subject"],
#         topic=data["topic"],
#         receipt_file_id=file_id,
#         user_telegram_id=msg.from_user.id,
#         status="PENDING"
#     )
#
#     caption = (
#         f"🆕 <b>Yangi buyurtma</b>\n\n"
#         f"🆔 ID: {order.id}\n"
#         f"👤 {order.fullname}\n"
#         f"📞 {order.phone}\n"
#         f"📘 {order.service}\n"
#         f"📚 {order.subject}\n"
#         f"📝 {order.topic}\n"
#         f"💰 {order.price}"
#     )
#
#     await send_func(
#         FIRST_CHANNEL_ID,
#         file_id,
#         caption=caption,
#         parse_mode="HTML",
#         reply_markup=first_channel_kb(order.id)
#     )
#
#     await msg.answer("✅ Chek qabul qilindi. Tekshirilmoqda...")
#     await state.clear()


# projectapp/ilmiy_vazifalar_bot/handlers/order_flow.py
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow
from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID
from projectapp.ilmiy_vazifalar_bot.handlers.first_channel import first_channel_kb

router = Router()

@router.message(OrderFlow.receipt, F.photo | F.document)
async def receipt(msg: Message, state: FSMContext, bot):
    data = await state.get_data()

    # Fayl aniqlash
    if msg.photo:
        file_id = msg.photo[-1].file_id
        send_func = bot.send_photo
    else:
        file_id = msg.document.file_id
        send_func = bot.send_document

    # Buyurtma yaratish
    order = await sync_to_async(Order.objects.create)(
        fullname=data["fullname"],
        phone=data["phone"],
        service=data["service"],
        price=data["price"],
        subject=data["subject"],
        topic=data["topic"],
        receipt_file_id=file_id,
        user_telegram_id=msg.from_user.id,
        status="PENDING"
    )

    # First channel caption
    caption = (
        f"🆕 <b>Yangi buyurtma</b>\n\n"
        f"🆔 ID: {order.id}\n"
        f"👤 {order.fullname}\n"
        f"📞 {order.phone}\n"
        f"📘 Xizmat: {order.service}\n"
        f"📚 Fan: {order.subject}\n"
        f"📝 Mavzu: {order.topic}\n"
        f"💰 {order.price}"
    )

    await send_func(
        FIRST_CHANNEL_ID,
        file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=first_channel_kb(order.id)
    )

    await msg.answer("✅ Chek qabul qilindi. Tekshirilmoqda...")
    await state.clear()
