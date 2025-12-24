from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.config import SECOND_CHANNEL_ID

router = Router()


# =========================
# FIRST CHANNEL TUGMALARI
# =========================
def first_channel_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ To‘lovni tasdiqlash",
                    callback_data=f"admin_accept:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ To‘lovni bekor qilish",
                    callback_data=f"payment_reject:{order_id}"
                )
            ]
        ]
    )


# =========================
# SECOND CHANNEL TUGMALARI
# =========================
def second_channel_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Qabul qildim",
                    callback_data=f"work_accept:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Buyurtmani yuborish",
                    callback_data=f"send_order:{order_id}"
                )
            ]
        ]
    )


# =========================
# TO‘LOVNI TASDIQLASH
# =========================
@router.callback_query(F.data.startswith("admin_accept:"))
async def admin_accept(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    if order.status != "PENDING":
        await cb.answer("Allaqachon tekshirilgan", show_alert=True)
        return

    order.status = "PAID"
    await sync_to_async(order.save)()

    await cb.message.edit_reply_markup()

    await bot.send_message(
        chat_id=int(order.user_telegram_id),
        text=f"✅ Buyurtma #{order.id} to‘lovi tasdiqlandi.\n📦 Tayyorlanmoqda"
    )

    await bot.send_message(
        chat_id=SECOND_CHANNEL_ID,
        text=(
            f"🆕 Yangi buyurtma\n\n"
            f"🆔 ID: {order.id}\n"
            f"👤 {order.fullname}\n"
            f"📞 {order.phone}\n"
            f"📘 Xizmat: {order.service}\n"
            f"📚 Fan: {order.subject}\n"
            f"📝 Mavzu: {order.topic}\n"
            f"💰 To‘lov tasdiqlandi"
        ),
        reply_markup=second_channel_kb(order.id)
    )

    await cb.answer("✅ Tasdiqlandi")


# =========================
# TO‘LOVNI BEKOR QILISH
# =========================
@router.callback_query(F.data.startswith("payment_reject:"))
async def payment_reject(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    if order.status != "PENDING":
        await cb.answer("Allaqachon tekshirilgan", show_alert=True)
        return

    order.status = "REJECTED"
    await sync_to_async(order.save)()

    await bot.send_message(
        chat_id=int(order.user_telegram_id),
        text=(
            "❌ <b>To‘lovingiz tasdiqlanmadi</b>\n\n"
            "Iltimos, to‘lovni tekshirib qayta urinib ko‘ring yoki admin bilan bog‘laning."
        ),
        parse_mode="HTML"
    )

    await cb.message.edit_reply_markup()
    await cb.answer("To‘lov bekor qilindi ❌", show_alert=True)
