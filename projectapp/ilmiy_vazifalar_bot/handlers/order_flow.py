from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from projectapp.ilmiy_vazifalar_bot.states import OrderFlow
from projectapp.ilmiy_vazifalar_bot.config import SERVICE_PRICES
from projectapp.models import Order

router = Router()

@router.message(F.text)
async def handle_service(msg: Message, state: FSMContext):
    data = await state.get_data()
    service = msg.text.lower()

    price = SERVICE_PRICES.get(service)
    await state.update_data(service=service, price=price)
    await msg.answer(f"{service.capitalize()} tanlandi! Narxi: {price if price else 'Kelishiladi'} so‘m.\nIltimos, ism va familiyangizni kiriting:")
    await state.set_state(OrderFlow.fullname)

@router.message(F.text, OrderFlow.fullname)
async def handle_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullname=msg.text)
    await msg.answer("Fanni nomini kiriting:")
    await state.set_state(OrderFlow.subject)

@router.message(F.text, OrderFlow.subject)
async def handle_subject(msg: Message, state: FSMContext):
    await state.update_data(subject=msg.text)
    await msg.answer("Mavzuni kiriting:")
    await state.set_state(OrderFlow.topic)

@router.message(F.text, OrderFlow.topic)
async def handle_topic(msg: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.objects.create(
        user_telegram_id=msg.from_user.id,
        contact_phone=data["contact"],
        service_type=data["service"],
        fullname=data["fullname"],
        subject=data["subject"],
        topic=msg.text,
        price=data["price"]
    )
    await msg.answer(f"Buyurta qabul qilindi!\n\nIsm: {order.fullname}\nFan: {order.subject}\nMavzu: {order.topic}\nNarx: {order.price} so‘m\nTo‘lovni amalga oshiring: 9860350101959046 Farmonov Faxriddin")
    await state.clear()
