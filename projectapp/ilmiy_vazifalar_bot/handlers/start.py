from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from aiogram.fsm.context import FSMContext
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow

router = Router()


# 1️⃣ /start — tanishtirish + kontakt tugmasi
@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Kontaktni ulashish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await msg.answer(
        "🎓 *Talabamisiz?*\n\n"
        "Unda biz sizga yordam beramiz 👇\n\n"
        "📌 Kurs ishlari\n"
        "📌 Mustaqil ishlar\n"
        "📌 Diplom ishlari\n"
        "📌 Amaliy ishlar va deadline topshiriqlar\n\n"
        
        "⬇️ Davom etish uchun kontaktni ulashing",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await state.set_state(OrderFlow.contact)


# 2️⃣ Kontakt qabul qilish → xizmatlar
@router.message(OrderFlow.contact)
async def contact_received(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("❗ Iltimos, pastdagi tugma orqali kontakt ulashing.")
        return

    await state.update_data(phone=msg.contact.phone_number)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Kurs ishi")],
            [KeyboardButton(text="📗 Mustaqil ish")],
            [KeyboardButton(text="🎓 Diplom ishi")],
            [KeyboardButton(text="💻 Dasturiy vositalar")]
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "✅ Rahmat!\n\n"
        "Quyidagi xizmatlardan birini tanlang 👇",
        reply_markup=kb
    )

    await state.set_state(OrderFlow.service)


# 3️⃣ Xizmat tanlash → Ism Familiya
@router.message(OrderFlow.service)
async def service_chosen(msg: Message, state: FSMContext):
    service = msg.text

    prices = {
        "📘 Kurs ishi": "150 000 so‘m",
        "📗 Mustaqil ish": "80 000 so‘m",
        "🎓 Diplom ishi": "500 000 so‘m",
        "💻 Dasturiy vositalar": "Kelishiladi"
    }

    if service not in prices:
        await msg.answer("❗ Iltimos, xizmatni tugmachadan tanlang.")
        return

    await state.update_data(
        service=service,
        price=prices[service]
    )

    await msg.answer(
        f"💰 Narxi: {prices[service]}\n\n"
        "✍️ Ism va Familiyangizni kiriting:"
    )

    await state.set_state(OrderFlow.fullname)


# 4️⃣ Ism–Familiya
@router.message(OrderFlow.fullname)
async def fullname_received(msg: Message, state: FSMContext):
    if len(msg.text.split()) < 2:
        await msg.answer("❗ Ism va Familiyani to‘liq kiriting.")
        return

    await state.update_data(fullname=msg.text)

    await msg.answer("📚 Fan nomini kiriting:")
    await state.set_state(OrderFlow.subject)


# 5️⃣ Fan
@router.message(OrderFlow.subject)
async def subject_received(msg: Message, state: FSMContext):
    await state.update_data(subject=msg.text)

    await msg.answer("📝 Mavzuni kiriting:")
    await state.set_state(OrderFlow.topic)


# 6️⃣ Mavzu → to‘lov
@router.message(OrderFlow.topic)
async def topic_received(msg: Message, state: FSMContext):
    await state.update_data(topic=msg.text)

    await msg.answer(
        "💳 To‘lovni amalga oshiring:\n"
        "📌 9860 3501 0195 9046\n\n"
        "📸 Chek rasmini yoki 📄 PDF faylni yuboring."
    )

    await state.set_state(OrderFlow.receipt)
