import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types.message import ContentType
import logging
import datetime
from config import TOKEN, PAYMENT_TOKEN, CHAT_ID
from file_of_button import kb_sussed_pay, kb_send_number_phone
import sql_for_dimacoin

logging.basicConfig(level=logging.INFO)


storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)

PRICE = types.LabeledPrice(label='Подписка на 1 месяц в копейках - ', amount=500*100)   # в копейках

support = ['флешки', 'наушники', 'мышки', 'провода', 'видеокарты']
for_help_cmd = ['что', 'не понимаю', 'блин', 'аа', 'help']


class Register(StatesGroup):
    desc = State()


@dp.message_handler(content_types=["new_chat_members"])
async def new_user(message: types.Message):
    await sql_for_dimacoin.new_user(user_id=message.from_user.id)
    while True:
        d1 = datetime.datetime.today()
        if d1.strftime("%m%d%S") == "010100":  # в 1 января 00 секунд будет +20 Dimacoin
            await sql_for_dimacoin.update_count_all(money=20)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply('/buy_500 - для пополнения средств\n'
                        '/desc - для того что бы ты отправил адрес\n'
                        '<code>Цены</code> - для того что бы узнать цены товаров\n'
                        '<code>Мой баланс</code> - для того что бы отобразить твой баланс\n', parse_mode='html')
    while True:
        await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=100)
        await asyncio.sleep(10)
        sel_time = await sql_for_dimacoin.sel_time(user_id=message.from_user.id)
        type(int(sel_time[0]))
        if int(sel_time[0]) >= 2000:
            await message.answer('Напиши мне!')
            await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-2500)


@dp.message_handler(Text('Мой баланс'))
async def cmd_my_balance(message: types.Message):
    await bot.send_photo(message.from_user.id, photo='https://yandex.ru/images/search?pos=1&from=tabbar&img_url=http%3A%2F%2Favatars.yandex.net%2Fget-music-content%2F2114230%2F1bd0db8b.a.9434830-1%2Fm1000x1000%3Fwebp%3Dfalse&text=dima+money&rpt=simage&lr=10846')
    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    await message.answer(f" 🤑 Твой ca$h - <i><b>{check[0]}</b></i> 🤑", parse_mode='html')


@dp.message_handler(Text('Цены'))
async def cmd_prices(message: types.Message):
    await message.answer('В dimacoin`ах\n'
                         '_______________\n'
                         'Флешки - 150\n'
                         'Наушники - 80\n'
                         'Мышки - 15\n'
                         'Провода - 50\n'
                         'Видеокарты - 5\n')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-20)


@dp.message_handler(commands=['buy_500'])
async def cmd_buy(message: types.Message):
    if PAYMENT_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.from_user.id, text='This is TEST!')
    # send_invoice -
    await bot.send_invoice(title='Подписка на бота!',
                           description='Еже месячная оплата\nВ размере 500 рублей',
                           provider_token=PAYMENT_TOKEN,
                           currency='rub',
                           photo_url='https://avatars.mds.yandex.net/i?id=e665ce9a6cb3c54ba459bcfa9c52366e-3861166-images-thumbs&n=13',
                           photo_size=416,
                           photo_width=416,
                           photo_height=234,
                           is_flexible=False,   # True только когда конечная цена зависит от доставки
                           prices=[PRICE],
                           start_parameter='one-mouth-subscription',
                           payload='test-invoice-payload',
                           chat_id=message.from_user.id)
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-250)


@dp.pre_checkout_query_handler(lambda query: True)   # Обрабатывается после 1 запроса user`a
async def pre_check(pre_c_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_c_q.id, ok=True)   # Нужно ответить за 10 сек или платёж будет остановлен


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def success_payment(message: types.Message):
    print('SUCCESSFUL PAY:')
    payment_into = message.successful_payment.to_python()
    for f, v in payment_into.items():
        print(f'{f} = {v}')
    await bot.send_message(message.chat.id,
                           f'Платёж на:{message.successful_payment.total_amount // 100} {message.successful_payment.currency}\n прошёл успешно, + 150 DIMaCOIN')
    await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=150)
    await message.answer("Ты можешь купить товары!", reply_markup=kb_sussed_pay)
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-250)


@dp.message_handler(commands=["Флешки"])
async def cmd_buy(message: types.Message):
    args = message.get_args()
    try:
        get_number = int(args)
    except (ValueError, TypeError):
        return await message.answer("Напиши например так: Флешки 1")

    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    if check[0] >= 150 * get_number:
        await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=-150 * get_number)
        description = await sql_for_dimacoin.sel_desc(user_id=message.from_user.id)
        if description != "NO":
            await message.reply("Успешно! Ждите отправки в течении 3х суток")
            await bot.send_message(CHAT_ID, f'Флешки {get_number} - {description[0]}')
            if get_number >= 5:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=10)
                await message.answer('Кэш бэк 10 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=20)
                await message.answer('Кэш бэк 20 DimaCoins')
            if get_number >= 20:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=30)
                await message.answer('Кэш бэк 30 DimaCoins')
        else:
            await message.reply('Введи описание!')
    else:
        await message.answer('Ошибка! Недостаточно средств на балансе!!')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-250)


@dp.message_handler(commands=["Наушники"])
async def cmd_buy(message: types.Message):
    args = message.get_args()
    try:
        get_number = int(args)
    except (ValueError, TypeError):
        return await message.answer("Напиши например так: Наушники 1")

    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    if check[0] >= 80 * get_number:
        await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=-80 * get_number)
        description = await sql_for_dimacoin.sel_desc(user_id=message.from_user.id)
        if description != "NO":
            await message.reply("Успешно! Ждите отправки в течении 3х суток")
            await bot.send_message(CHAT_ID, f'Наушники {get_number} - {description[0]}')
            if get_number >= 5:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=10)
                await message.answer('Кэш бэк 10 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=20)
                await message.answer('Кэш бэк 20 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=30)
                await message.answer('Кэш бэк 30 DimaCoins')
        else:
            await message.reply('Введи описание!')
    else:
        await message.answer('Ошибка! Недостаточно средств на балансе!!')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-200)


@dp.message_handler(commands=["Мышки"])
async def cmd_buy(message: types.Message):
    args = message.get_args()
    try:
        get_number = int(args)
    except (ValueError, TypeError):
        return await message.answer("Напиши например так: Мышки 1")

    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    if check[0] >= 15 * get_number:
        await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=-15 * get_number)
        description = await sql_for_dimacoin.sel_desc(user_id=message.from_user.id)
        if description != "NO":
            await message.reply("Успешно! Ждите отправки в течении 3х суток")
            await bot.send_message(CHAT_ID, f'Мышки {get_number} - {description[0]}')
            if get_number >= 5:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=10)
                await message.answer('Кэш бэк 10 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=20)
                await message.answer('Кэш бэк 20 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=30)
                await message.answer('Кэш бэк 30 DimaCoins')
        else:
            await message.reply('Введи описание!')
    else:
        await message.answer('Ошибка! Недостаточно средств на балансе!!')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-500)


@dp.message_handler(commands=["Провода"])
async def cmd_buy(message: types.Message):
    args = message.get_args()
    try:
        get_number = int(args)
    except (ValueError, TypeError):
        return await message.answer("Напиши например так: Провода 1")

    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    if check[0] >= 50 * get_number:
        await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=-50 * get_number)
        description = await sql_for_dimacoin.sel_desc(user_id=message.from_user.id)
        if description != "NO":
            await message.reply("Успешно! Ждите отправки в течении 3х суток")
            await bot.send_message(CHAT_ID, f'Провода {get_number} - {description[0]}')
            if get_number >= 5:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=10)
                await message.answer('Кэш бэк 10 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=20)
                await message.answer('Кэш бэк 20 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=30)
                await message.answer('Кэш бэк 30 DimaCoins')
        else:
            await message.reply('Введи описание!')
    else:
        await message.answer('Ошибка! Недостаточно средств на балансе!!')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-25)


@dp.message_handler(commands=["Видеокарты"])
async def cmd_buy(message: types.Message):
    args = message.get_args()
    try:
        get_number = int(args)
    except (ValueError, TypeError):
        return await message.answer("Напиши например так: Видеокарты 1")

    check = await sql_for_dimacoin.sel_count(user_id=message.from_user.id)
    if check[0] >= 5 * get_number:
        await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=-5 * get_number)
        description = await sql_for_dimacoin.sel_desc(user_id=message.from_user.id)
        if description != "NO":
            await message.reply("Успешно! Ждите отправки в течении 3х суток")
            await bot.send_message(CHAT_ID, f'Видеокарты {get_number} - {description[0]}')
            if get_number >= 5:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=10)
                await message.answer('Кэш бэк 10 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=20)
                await message.answer('Кэш бэк 20 DimaCoins')
            if get_number >= 10:
                await sql_for_dimacoin.update_count(user_id=message.from_user.id, money=30)
                await message.answer('Кэш бэк 30 DimaCoins')
        else:
            await message.reply('Введи описание!')
    else:
        await message.answer('Ошибка! Недостаточно средств на балансе!!')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-550)


@dp.message_handler(commands=['desc'])
async def cmd_desc(message: types.Message):
    await message.answer('Ок! Введи улицу, город, номер телефона(<b>Москва или Котлас</b>)', parse_mode='html')
    await Register.desc.set()
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=-234)


@dp.message_handler(state=Register.desc)
async def load_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await state.finish()
    await message.reply(text=f'<b>Вот твои данные</b>: {data["desc"]}', parse_mode='html')
    await sql_for_dimacoin.update_desc(user_id=message.from_user.id, desc=str(data['desc']))
        # await bot.send_message(chat_id=CHAT_ID, text=f'{data["desc"]}')


@dp.message_handler()
async def all_txt(message: types.Message):
    text = message.text.lower()
    for word in for_help_cmd:
        if word in text:
            await message.answer('Сначала платёж, далее /desc, покупка вещи(пример: /Мышки 1), ну и ждёшь пока она придёт\n'
                                 '(у нас есть группа куда сливаются эти данные и к тебе приходит товар).', reply_markup=kb_send_number_phone)
    for word in support:
        if word in text:
            await message.answer('Сначала платёж, далее /desc, покупка вещи(пример: /Мышки 1), ну и ждёшь пока она придёт\n'
                                 '(у нас есть группа куда сливаются эти данные и к тебе приходит товар).')
    await sql_for_dimacoin.update_time(user_id=message.from_user.id, seconds=1)


async def on_startup(_):
    await sql_for_dimacoin.db_conn()
    print("OK! DB CONNECT")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)   # ЧТО БЫ НЕ ПРОПУСТИТЬ НИ ОДНОГО СООБЩЕНИЯ!!!