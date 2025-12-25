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
# START TUGMASI
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
# ✅ QABUL QILDIM
# =========================
@router.callback_query(F.data.startswith("work_accept:"))
async def work_accept(cb: CallbackQuery):
    order_id = int(cb.data.split(":")[1])

    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        await cb.answer("Buyurtma topilmadi", show_alert=True)
        return

    order.status = "IN_PROGRESS"
    await sync_to_async(order.save)()

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
    await cb.answer("✅ Buyurtma sizga biriktirildi", show_alert=True)

# =========================
# 📤 BUYURTMANI YUBORISH
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
# 📎 CHANNEL'DAN KELGAN NATIJA
# 🔥 ASOSIY MUHIM QISM
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

    # =========================
    # FILE ANIQLASH
    # =========================
    if msg.photo:
        tg_file = msg.photo[-1]
        file_id = tg_file.file_id
        filename = f"order_{order_id}.jpg"
    elif msg.document:
        tg_file = msg.document
        file_id = tg_file.file_id
        filename = tg_file.file_name or f"order_{order_id}"
    else:
        return

    # =========================
    # TELEGRAM'DAN FILE YUKLAB OLISH
    # =========================
    tg_file_obj = await bot.get_file(file_id)
    file_bytes = await bot.download_file(tg_file_obj.file_path)

    # =========================
    # 🔥 DB GA REAL FILE SAQLASH
    # =========================
    order.result_tg_file_id = file_id
    order.result_file.save(
        filename,
        ContentFile(file_bytes.read()),
        save=False
    )
    order.status = "DONE"
    await sync_to_async(order.save)()

    # =========================
    # MIJOZGA FILE YUBORISH
    # =========================
    if msg.photo:
        await bot.send_photo(order.user_telegram_id, photo=file_id)
    else:
        await bot.send_document(order.user_telegram_id, document=file_id)

    await bot.send_message(
        order.user_telegram_id,
        (
            f"✅ Buyurtma #{order.id} tayyor!\n"
            f"📎 Fayl yuborildi.\n"
            f"Rahmat! taklif va shikoyatlar uchun t.me/takliflar_va_shikoyatlar ga yozing !!!"
        ),
        reply_markup=start_kb
    )

# =========================
# SECOND CHANNELGA BUYURTMA YUBORISH
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

    await bot.send_message(
        chat_id=-1003387576321,
        text=text,
        reply_markup=second_channel_kb(order.id)
    )
