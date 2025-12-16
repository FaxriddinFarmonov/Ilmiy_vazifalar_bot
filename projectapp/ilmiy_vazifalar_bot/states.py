from aiogram.fsm.state import StatesGroup, State

class OrderFlow(StatesGroup):
    contact = State()
    service = State()
    fullname = State()
    subject = State()
    topic = State()
    payment = State()
