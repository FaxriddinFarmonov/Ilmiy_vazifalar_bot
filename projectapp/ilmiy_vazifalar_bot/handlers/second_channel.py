from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from asgiref.sync import sync_to_async
from projectapp.models import Order

router = Router()

# =====================================================
# 🔘 SECOND CHANNEL TUGMALARI
# =====================================================
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

# =====================================================
# ✅ QABUL QILDIM
# =====================================================
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

# =====================================================
# 📤 BUYURTMANI YUBORISH
# =====================================================
@router.callback_query(F.data.startswith("send_order:"))
async def send_order(cb: CallbackQuery):
    order_id = int(cb.data.split(":")[1])

    await cb.message.answer(
        f"📎 Buyurtma #{order_id} faylini yuboring\n\n"
        f"⚠️ Caption aniq shunday bo‘lsin:\n"
        f"order:{order_id}"
    )
    await cb.answer()

# =====================================================
# 📎 MUHIM QISM ❗
# CHANNEL'DAN KELGAN POSTNI USHLASH
# =====================================================
@router.channel_post(F.document | F.photo)
async def send_result(channel_post: Message, bot):
    # caption majburiy
    if not channel_post.caption or not channel_post.caption.startswith("order:"):
        return

    try:
        order_id = int(channel_post.caption.split(":")[1])
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except (ValueError, Order.DoesNotExist):
        return

    # Fayl aniqlash
    if channel_post.photo:
        file_id = channel_post.photo[-1].file_id
        await bot.send_photo(
            chat_id=order.user_telegram_id,
            photo=file_id
        )
    elif channel_post.document:
        file_id = channel_post.document.file_id
        await bot.send_document(
            chat_id=order.user_telegram_id,
            document=file_id
        )
    else:
        return

    # Status va DB
    order.result_file_id = file_id
    order.status = "DONE"
    await sync_to_async(order.save)()

    # Mijozga xabar
    await bot.send_message(
        order.user_telegram_id,
        f"✅ Buyurtma #{order.id} tayyor!\n📎 Fayl yuborildi.\nRahmat!"
    )
