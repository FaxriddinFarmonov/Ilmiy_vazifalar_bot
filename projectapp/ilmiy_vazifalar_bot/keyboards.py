from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Kontaktni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

def services_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Kurs ishi")],
            [KeyboardButton(text="📗 Mustaqil ish")],
            [KeyboardButton(text="🎓 Diplom ishi")],
            [KeyboardButton(text="💻 Dasturiy vositalar")]
        ],
        resize_keyboard=True
    )

def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Hammasi to‘g‘ri", callback_data="confirm_yes")],
            [InlineKeyboardButton(text="❌ Xato bor", callback_data="confirm_no")]
        ]
    )
