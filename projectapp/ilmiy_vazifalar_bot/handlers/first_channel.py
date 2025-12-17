# projectapp/ilmiy_vazifalar_bot/handlers/first_channel.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from projectapp.models import Order
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow
from projectapp.ilmiy_vazifalar_bot.config import FIRST_CHANNEL_ID, SECOND_CHANNEL_ID

router = Router()

# =========================
# 🔘 FIRST KANAL ADMIN TUGMASI
# =========================
def admin_confirm_kb(order_id: int):
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

# =========================
# 💳 CHEK QABUL QILISH
# =========================
@router.message(OrderFlow.receipt, F.photo | F.document)
async def receipt(msg: Message, state: FSMContext, bot):
    data = await state.get_data()

    # Fayl turi tekshirish
    file_id = None
    file_type = None
    if msg.photo:
        file_id = msg.photo[-1].file_id
        file_type = "photo"
    elif msg.document:
        file_id = msg.document.file_id
        file_type = "document"

    # Order yaratish (modelga mos)
    order = await sync_to_async(Order.objects.create)(
        fullname=data.get("fullname"),
        phone=data.get("phone"),
        service=data.get("service"),
        price=data.get("price"),
        subject=data.get("subject"),
        topic=data.get("topic"),
        receipt_file_id=file_id,
        status="PENDING"
    )

    # 1-kanalga yuborish matni + inline tugma
    text = (
        f"🆕 <b>Yangi buyurtma!</b>\n\n"
        f"👤 Ism: {order.fullname}\n"
        f"📞 Tel: {order.phone}\n"
        f"📘 Xizmat: {order.service}\n"
        f"📚 Fan: {order.subject}\n"
        f"📝 Mavzu: {order.topic}\n"
        f"💰 Narxi: {order.price}"
    )

    await bot.send_message(
        FIRST_CHANNEL_ID,
        text,
        parse_mode="HTML",
        reply_markup=admin_confirm_kb(order.id)
    )

    # Faylni yuborish
    if file_id:
        if file_type == "photo":
            await bot.send_photo(FIRST_CHANNEL_ID, file_id)
        elif file_type == "document":
            await bot.send_document(FIRST_CHANNEL_ID, file_id)

    # Foydalanuvchiga xabar
    await msg.answer("✅ Chek qabul qilindi. Tekshirilmoqda...")

    # FSM state ni tozalash
    await state.clear()


# =========================
# ✅ ADMIN TO'LOVNI TASDIQLADI
# =========================
from aiogram.types import CallbackQuery

@router.callback_query(F.data.startswith("admin_accept:"))
async def admin_accept(cb: CallbackQuery, bot):
    order_id = int(cb.data.split(":")[1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    if order.status != "PENDING":
        await cb.answer("❌ Bu buyurtma allaqachon tasdiqlangan", show_alert=True)
        return

    order.status = "PAID"
    order.accepted_by = cb.from_user.full_name
    await sync_to_async(order.save)()

    # Inline tugmani o'chirish
    await cb.message.edit_reply_markup()

    # 👤 Mijozga xabar
    if hasattr(order, "user_telegram_id"):
        tg_id = order.user_telegram_id
    else:
        tg_id = cb.from_user.id
    await bot.send_message(tg_id, "✅ To‘lovingiz tasdiqlandi.\n📦 Buyurtmangiz tayyorlanmoqda.")

    # 📤 2-kanalga xabar
    text_2channel = (
        f"🆕 <b>Yangi buyurtma</b>\n\n"
        f"👤 <b>{order.fullname}</b>\n"
        f"📘 Xizmat: {order.service}\n"
        f"📚 Fan: {order.subject}\n"
        f"📝 Mavzu: {order.topic}\n\n"
        f"💰 <b>To‘lov tasdiqlandi</b>\n"
        f"👨‍💼 Admin: {cb.from_user.full_name}"
    )

    # ❗ SECOND_CHANNEL_ID to‘g‘ri ekanligiga ishonch hosil qiling (private kanal bo‘lsa bot admin bo‘lishi kerak)
    await bot.send_message(
        SECOND_CHANNEL_ID,
        text_2channel,
        parse_mode="HTML"
    )

    await cb.answer("✅ To‘lov tasdiqlandi")
