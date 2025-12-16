from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow

router = Router()

# Boshlang'ich /start
@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="📱 Kontaktni ulashish",
            request_contact=True
        )]],
        resize_keyboard=True
    )
    await msg.answer(
        "Assalomu alaykum! Iltimos, kontaktni ulashing.",
        reply_markup=kb
    )
    await state.set_state(OrderFlow.contact)


# Kontakt qabul qilgandan keyin xizmatlar tugmachalari
@router.message(OrderFlow.contact)
async def contact_received(msg: Message, state: FSMContext):
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
        "Assalomu alaykum!\n\nUniversitetda o‘qiysizmi?\nUnda biz sizga yordam beramiz 👇",
        reply_markup=kb
    )
    await state.set_state(OrderFlow.service)


# Xizmat tanlanganida narx va ism-familiyani so‘rash
@router.message(OrderFlow.service)
async def service_chosen(msg: Message, state: FSMContext):
    service = msg.text
    await state.update_data(service=service)

    # Narx va matnni aniqlash
    if service == "📘 Kurs ishi":
        text = "Narxi: 150 000 so‘m\n\nBuyurtma berish uchun iltimos, Ism va Familiyangizni kiriting:"
    elif service == "📗 Mustaqil ish":
        text = "Narxi: 80 000 so‘m\n\nBuyurtma berish uchun iltimos, Ism va Familiyangizni kiriting:"
    elif service == "🎓 Diplom ishi":
        text = "Narxi: 500 000 so‘m\n\nBuyurtma berish uchun iltimos, Ism va Familiyangizni kiriting:"
    elif service == "💻 Dasturiy vositalar":
        text = "Narxi: kelishiladi\n\nBuyurtma berish uchun iltimos, Ism va Familiyangizni kiriting:"
    else:
        text = "Iltimos, xizmatni tugmachadan tanlang."

    await msg.answer(text)
    await state.set_state(OrderFlow.fullname)
