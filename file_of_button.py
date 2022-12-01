from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb_sussed_pay = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('/Флешки')
b2 = KeyboardButton('/Наушники')
b3 = KeyboardButton('/Мышки')
b4 = KeyboardButton('/Провода')
b5 = KeyboardButton('/Видеокарты')
kb_sussed_pay.add(b1, b2, b3, b4, b5)

kb_send_number_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отправить свой контакт ☎️', request_contact=True))