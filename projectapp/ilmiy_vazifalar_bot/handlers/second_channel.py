from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from projectapp.models import Order

router = Router()

# =========================
# 🔘 TUGMALAR
# =========================
def second_channel_keyboard(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Qabul qildim",
                    callback_data=f"work_started:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Tayyor, mijozga yuborish",
                    callback_data=f"work_done:{order_id}"
                )
            ]
        ]
    )

# =========================
# 📥 ISH BOSHLANDI
# =========================
@router.callback_query(F.data.startswith("work_started:"))
async def work_started(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])

    order = Order.objects.get(id=order_id)

    if order.status != "PAID":
        await cb.answer("❌ To‘lov hali tasdiqlanmagan", show_alert=True)
        return

    order.status = "IN_PROGRESS"
    order.taken_by = cb.from_user.full_name
    order.save()

    # 👤 MIJOZGA XABAR
    await bot.send_message(
        order.user.telegram_id,
        "📦 Buyurtmangiz qabul qilindi.\nIsh boshlandi."
    )

    await cb.answer("✅ Ish boshlandi")

# =========================
# 📤 ISH TAYYOR
# =========================
@router.callback_query(F.data.startswith("work_done:"))
async def work_done(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])
    order = Order.objects.get(id=order_id)

    if order.status != "IN_PROGRESS":
        await cb.answer("❌ Ish hali boshlanmagan", show_alert=True)
        return

    order.status = "DONE"
    order.completed_by = cb.from_user.full_name
    order.save()

    await bot.send_message(
        order.user.telegram_id,
        "✅ Buyurtmangiz tayyor!\nAdmin tez orada faylni yuboradi."
    )

    await cb.answer("📤 Tayyor deb belgilandi")
