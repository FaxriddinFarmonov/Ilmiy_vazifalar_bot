from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from projectapp.models import Order

router = Router()

# =========================
# START TUGMASI (MIJOZ UCHUN)
# =========================
start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]],
    resize_keyboard=True
)

# =========================
# INLINE TUGMALAR
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
# ✅ QABUL QILDIM HANDLER
# =========================
@router.callback_query(F.data.startswith("work_accept:"))
async def work_accept(cb: CallbackQuery):
    order_id = int(cb.data.split(":")[1])
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ Qabul qildi: {cb.from_user.full_name}",
                    callback_data="none"
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
    await cb.message.edit_reply_markup(reply_markup=kb)
    await cb.answer("✅ Buyurtma qabul qilindi", show_alert=True)

# =========================
# 📤 BUYURTMANI YUBORISH HANDLER
# =========================
@router.callback_query(F.data.startswith("send_order:"))
async def send_order(cb: CallbackQuery):
    order_id = int(cb.data.split(":")[1])
    await cb.message.answer(
        f"📎 Buyurtma #{order_id} faylini yuboring\n\n"
        f"⚠️ Caption AYNAN shunday bo‘lsin:\n"
        f"order:{order_id}"
    )
    await cb.answer()

# =========================
# 📎 CHANNEL'DAN KELGAN FILE
# =========================
@router.channel_post(F.photo | F.document)
async def result_from_channel(msg: Message, bot):
    if not msg.caption or not msg.caption.startswith("order:"):
        return
    try:
        order_id = int(msg.caption.split(":")[1])
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except (ValueError, Order.DoesNotExist):
        return

    # Faylni aniqlash
    if msg.photo:
        file_id = msg.photo[-1].file_id
        await bot.send_photo(chat_id=order.user_telegram_id, photo=file_id)
    elif msg.document:
        file_id = msg.document.file_id
        await bot.send_document(chat_id=order.user_telegram_id, document=file_id)
    else:
        return

    # DB yangilash
    order.result_tg_file_id = file_id
    order.status = "DONE"
    await sync_to_async(order.save)()

    # Mijozga xabar
    await bot.send_message(
        chat_id=order.user_telegram_id,
        text=(
            f"✅ Buyurtma #{order.id} tayyor!\n"
            f"📎 Fayl yuborildi.\n"
            f"Rahmat!\n"
            f"Talab va takliflar uchun @takliflar_va_shikoyatlar"
        ),
        reply_markup=start_kb
    )

# =========================
# SECOND CHANNELGA YUBORILADIGAN BUYURTMANI FORMAT
# =========================
async def send_order_to_second_channel(order: Order, bot):
    text = (
        f"🆕 Yangi buyurtma\n\n"
        f"🆔 ID: {order.id}\n"
        f"👤 {order.fullname}\n"
        f"📞 {order.phone}\n"
        f"📘 Xizmat: {order.service}\n"
        f"📚 Fan: {order.subject}\n"
        f"📝 Mavzu: {order.topic}\n"
        f"💰 To‘lov tasdiqlandi\n\n"
        f"📎 Natijani yuborishda caption yozing:\n"
        f"order:{order.id}"
    )

    # 1️⃣ Buyurtma matni yuboriladi
    message = await bot.send_message(
        chat_id=-1003387576321,  # Kanal ID
        text=text
    )

    # 2️⃣ Inline tugmalar qo‘shiladi har bir buyurtma uchun alohida
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=second_channel_kb(order.id)
    )
