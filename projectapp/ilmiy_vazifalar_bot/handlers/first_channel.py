# from aiogram import Router, F
# from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# from asgiref.sync import sync_to_async
# from projectapp.models import Order
# from projectapp.ilmiy_vazifalar_bot.config import SECOND_CHANNEL_ID
# from projectapp.ilmiy_vazifalar_bot.handlers.second_channel import second_channel_kb
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
# @router.callback_query(F.data.startswith("admin_accept:"))
# async def admin_accept(cb: CallbackQuery, bot):
#     order_id = int(cb.data.split(":")[1])
#     order = await sync_to_async(Order.objects.get)(id=order_id)
#
#     if order.status != "PENDING":
#         await cb.answer("Allaqachon tekshirilgan", show_alert=True)
#         return
#
#     order.status = "PAID"
#     await sync_to_async(order.save)()
#
#     await cb.message.edit_reply_markup()
#
#     # 👤 MIJOZ
#     await bot.send_message(
#         order.user_telegram_id,
#         f"✅ Buyurtma #{order.id} to‘lovi tasdiqlandi.\n📦 Tayyorlanmoqda"
#     )
#
#     # 📢 SECOND CHANNEL (TO‘LIQ MA’LUMOT + TUGMALAR)
#     await bot.send_message(
#         SECOND_CHANNEL_ID,
#         (
#             f"📦 Buyurtma #{order.id}\n"
#             f"👤 Mijoz: {order.fullname}\n"
#             f"📘 Xizmat: {order.service}\n"
#             f"💰 To‘lov tasdiqlandi\n"
#             f"👨‍💼 Tasdiqladi: {cb.from_user.full_name}"
#         ),
#         reply_markup=second_channel_kb(order.id)
#     )
#
#     await cb.answer("Tasdiqlandi")


# projectapp/ilmiy_vazifalar_bot/handlers/first_channel.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.config import SECOND_CHANNEL_ID
from projectapp.ilmiy_vazifalar_bot.handlers.second_channel import second_channel_kb

router = Router()

def first_channel_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ To‘lovni tasdiqlash",
                    callback_data=f"admin_accept:{order_id}"
                )
            ]
        ]
    )

@router.callback_query(F.data.startswith("admin_accept:"))
async def admin_accept(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    if order.status != "PENDING":
        await cb.answer("Allaqachon tekshirilgan", show_alert=True)
        return

    # Statusni yangilash
    order.status = "PAID"
    await sync_to_async(order.save)()

    # Inline tugmani o‘chirish
    await cb.message.edit_reply_markup()

    # 👤 Mijozga xabar
    await bot.send_message(
        order.user_telegram_id,
        f"✅ Buyurtma #{order.id} to‘lovi tasdiqlandi.\n📦 Tayyorlanmoqda"
    )

    # 📢 Second channelga yuborish
    await bot.send_message(
        SECOND_CHANNEL_ID,
        (
            f"🆕 Yangi buyurtma\n\n"
            f"🆔 ID: {order.id}\n"
            f"👤 {order.fullname}\n"
            f"📞 {order.phone}\n"
            f"📘 Xizmat: {order.service}\n"
            f"📚 Fan:{order.subject}\n"
            f"📝 Mavzu: {order.topic}\n"
            f"💰 To‘lov tasdiqlandi\n"
            f"👨‍💼 Tasdiqladi: {cb.from_user.full_name}"
        ),
        reply_markup=second_channel_kb(order.id)
    )

    await cb.answer("✅ Tasdiqlandi")
