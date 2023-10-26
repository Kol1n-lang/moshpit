import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.message import ContentType
import cv2
from parser import generate_qr
from db import prizers, insert_prizes, insert_user
import sqlite3
from aiogram.types import InputFile
from db import find_photo_names
import os
from db import counts


PRICE = types.LabeledPrice('Билет на одного', amount=200*100)
PRICE2 = types.LabeledPrice('1+1', amount=300*100)
PRICE3 = types.LabeledPrice('VIP', amount=300*100)
PRICE4 = types.LabeledPrice('Premium', amount=1400*100)
class ClientState(StatesGroup):
    '''Хранит на каком этапе диалога находится клиент'''
    START_ORDER = State()
    INFO = State()
    NAME_SELECTED = State()
    BUY_TICKETONE = State()
    BUY_TICKETTWO = State()
    CHOOSETYPE = State()
    CHOOSETICKET = State()
    TRY_TO_PAY_1 = State()
    TRY_TO_PAY_2 = State()
    TRY_TO_PAY_3 = State()
    TRY_TO_PAY_4 = State()
    PRIZE = State()
    SUCCESFULLY_PAY = State()
    OTKAZ = State()
    OZHIDANIE = State()



bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

# storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
# storage = MongoStorage(host='localhost', port=27017, db_name='aiogram_fsm')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['Start'])
async def start_proccess(message: types.Message, state: FSMContext) -> None:
    msg = '''Привет! 👋🤖 Я бот для покупки билета на тусовку MOSHPIT'''

    buy_ticket = KeyboardButton('Купить билет')
    info = KeyboardButton('О нас')
    prize = KeyboardButton('Розыгрыш от MOSPIT')
    otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
    my_tickets = KeyboardButton('Мои билеты')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(buy_ticket, info)
    markup.row(prize, otzyv)
    markup.row(my_tickets)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_ORDER)


@dp.message_handler(state=ClientState.START_ORDER)
async def choose_doing(message: types.Message, state: FSMContext):
    user_msg = message.text
    if user_msg == 'Купить билет':
        await message.answer('Как вас зовут?')
        await state.set_state(ClientState.CHOOSETYPE)
    elif user_msg == 'О нас':
        await message.answer('Наша официальная группа, https://t.me/moshpit_yo')
        await state.set_state(ClientState.START_ORDER)
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        buy_ticket = KeyboardButton('Купить билет')
        prize = KeyboardButton('Розыгрыш от MOSPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(buy_ticket,prize)
        markup.row(otzyv, my_tickets)
        await message.answer('Что-то ещё?', reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
    elif user_msg == 'Розыгрыш от MOSPIT':
        markup1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        true = KeyboardButton('ДА')
        false = KeyboardButton('НЕТ')
        markup1.row(true, false)
        await message.answer('Хочешь участвовать?', reply_markup=markup1)
        await state.set_state(ClientState.PRIZE)
    elif message.text == 'Отзывы о сервисе и MOSHPIT':
        msg = '''Отзывов пока что нет'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(buy_ticket, info)
        markup.row(prize, my_tickets)
        await message.answer(msg, reply_markup=markup)
    elif message.text == 'Мои билеты':
        msg2 = 'Ты ещё ничего не купил'
        user1 = f'{message.from_user.id}' + '_standart.jpg'
        user2 = f'{message.from_user.id}' + '_1+1.jpg'
        uservip = f'{message.from_user.id}' + '_vip.jpg'
        userpremium = f'{message.from_user.id}' + '_premium.jpg'
        tickets1 = find_photo_names(user1)
        tickets2 = find_photo_names(user2)
        tickets3 = find_photo_names(uservip)
        tickets4 = find_photo_names(userpremium)
        if len(tickets1) != 0:
            count = counts(message.from_user.id, 'standart')
            await message.answer(f'Билеты на одного, количество : {count}')
            for standart in tickets1:
                photo = InputFile(f'qr_codes/{standart}')
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
        if len(tickets2) != 0:
            count = counts(message.from_user.id, '1+1')
            await message.answer(f'Билеты 1+1, количество : {count}')
            for oneone in tickets1:
                photo = InputFile(f'qr_codes/{oneone}')
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
        if len(tickets3) != 0:
            count = counts(message.from_user.id, 'vip')
            await message.answer(f'Билеты 1+1, количество : {count}')
            for oneone in tickets1:
                photo = InputFile(f'qr_codes/{oneone}')
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
        if len(tickets4) != 0:
            count = counts(message.from_user.id, 'premium')
            await message.answer(f'Билеты Premium, количество : {count}')
            for oneone in tickets1:
                photo = InputFile(f'qr_codes/{oneone}')
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
        if (len(tickets1) == 0) and (len(tickets3) == 0) and (len(tickets4) == 0) and (len(tickets2) == 0):
            await message.answer('Вы ещё не купили билеты')
        msg = '''Желаешь что-то ещё?'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSHPIT')
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(buy_ticket, info)
        markup.row(prize, otzyv)
        await message.answer(msg, reply_markup=markup)
    else:
        await message.answer('Я тебя не понимаю, нажми кнопку')

@dp.message_handler(state=ClientState.PRIZE)
async def prize_answer(message: types.Message, state: FSMContext):
    user_msg = message.text
    if user_msg == 'ДА':
        try:
            insert_prizes(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
            buy_ticket = KeyboardButton('Купить билет')
            info = KeyboardButton('О нас')
            otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
            my_tickets = KeyboardButton('Мои билеты')
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.row(buy_ticket, info)
            markup.row(my_tickets, otzyv)
            await message.answer(' Ты записан в число участников', reply_markup=markup)
            await state.set_state(ClientState.START_ORDER)
        except ValueError as e:
            await message.answer('Что-то пошло не так')
        await state.set_state(ClientState.START_ORDER)
    elif user_msg == 'НЕТ':
        await message.answer('Твоё желание,\n')
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(buy_ticket, info)
        markup.row(my_tickets, otzyv)
        await message.answer('Ты всегда можешь принять участие в наших розыгрышах', reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
    else:
        await message.answer('Я тебя не понимаю, нажми кнопку')
        await state.set_state(ClientState.PRIZE)
@dp.message_handler(state=ClientState.CHOOSETYPE)
async def choose(message: types.Message, state: FSMContext):
    msg = 'Выбери билет'
    one = KeyboardButton('Билет на одного')
    two = KeyboardButton('Билет 1+1')
    vip = KeyboardButton('VIP билет')
    premium = KeyboardButton('Premium билет')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(one, two)
    markup.row(vip, premium)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.CHOOSETICKET)
@dp.message_handler(state=ClientState.CHOOSETICKET)
async def choose_ticket(message: types.Message, state: FSMContext):
    if message.text == 'Билет на одного':
        await message.answer(f'Вот ссылка на оплату\nПосле оплаты мы отправим тебе QR-код\nдля входа на мероприятие')
        await bot.send_invoice(message.chat.id, 'Билет на одного',
                            'Билет на одного',
                            provider_token=config.PAY_TOCKEN,
                            currency='rub',
                            prices=[PRICE],
                            start_parameter='one-people-ticket',
                            payload='payload')
        otmena = KeyboardButton('Отмена')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(otmena)
        await message.answer('Отменить?', reply_markup=markup)
        await state.set_state(ClientState.TRY_TO_PAY_1)
    elif message.text == 'Билет 1+1':
        await message.answer(f'Вот ссылка на оплату\nПосле оплаты мы отправим тебе QR-код\nдля входа на мероприятие')
        await bot.send_invoice(message.chat.id, 'Билет для двоих',
                               'С другом всегда веселее)',
                               provider_token=config.PAY_TOCKEN,
                               currency='rub',
                               prices=[PRICE2],
                               start_parameter='oneone-people-ticket',
                               payload='payload')
        otmena = KeyboardButton('Отмена')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(otmena)
        await message.answer('Отменить?', reply_markup=markup)
        await state.set_state(ClientState.TRY_TO_PAY_2)
    elif message.text == 'VIP билет':
        await message.answer(f'Вот ссылка на оплату\nПосле оплаты мы отправим тебе QR-код\nдля входа на мероприятие')
        await bot.send_invoice(message.chat.id, 'Ранний вход',
                               'Проходка раньше остальных',
                               provider_token=config.PAY_TOCKEN,
                               currency='rub',
                               prices=[PRICE3],
                               start_parameter='one-people-ticket',
                               payload='payload')
        otmena = KeyboardButton('Отмена')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(otmena)
        await message.answer('Отменить?', reply_markup=markup)
        await state.set_state(ClientState.TRY_TO_PAY_3)
    elif message.text == 'Premium билет':
        await message.answer(f'Вот ссылка на оплату\nПосле оплаты мы отправим тебе QR-код\nдля входа на мероприятие')
        await bot.send_invoice(message.chat.id, 'Столик для 6 человек',
                               'Проходка раньше остальных',
                               provider_token=config.PAY_TOCKEN,
                               currency='rub',
                               prices=[PRICE4],
                               start_parameter='one-people-ticket',
                               payload='payload')
        otmena = KeyboardButton('Отмена')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(otmena)
        await message.answer('Отменить?', reply_markup=markup)
        await state.set_state(ClientState.TRY_TO_PAY_4)
    else:
        await message.answer('Я тебя не понимаю, нажми кнопку')
        await state.set_state(ClientState.CHOOSETICKET)

@dp.message_handler(text=['Отмена'], state=ClientState.TRY_TO_PAY_1)
async def otmena(message : types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 3)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
        msg = '''Вы отменили платёж'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSHPIT')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup.row(buy_ticket, info)
        markup.row(prize, otzyv)
        markup.row(my_tickets)
        await message.answer(msg, reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
@dp.pre_checkout_query_handler(lambda query: True, state=ClientState.TRY_TO_PAY_1)
async def pre_checkout_query(pre_chekout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_chekout_q.id, ok=True)
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=ClientState.TRY_TO_PAY_1)
async def successful_payment(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    payment_info = message.successful_payment.to_python()
    generate_qr(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'standart')
    insert_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'standart')
    photo = InputFile(f'qr_codes/{message.from_user.id}_standart.jpg')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    msg = '''Вы купили билет на одного'''
    buy_ticket = KeyboardButton('Купить билет')
    info = KeyboardButton('О нас')
    prize = KeyboardButton('Розыгрыш от MOSHPIT')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
    my_tickets = KeyboardButton('Мои билеты')
    markup.row(buy_ticket, info)
    markup.row(prize, otzyv)
    markup.row(my_tickets)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_ORDER)
@dp.message_handler(text=['Отмена'], state=ClientState.TRY_TO_PAY_2)
async def otmena(message : types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 3)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
        msg = '''Вы отменили платёж'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSHPIT')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup.row(buy_ticket, info)
        markup.row(prize, otzyv)
        markup.row(my_tickets)
        await message.answer(msg, reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
@dp.pre_checkout_query_handler(lambda query: True, state=ClientState.TRY_TO_PAY_2)
async def pre_checkout_query(pre_chekout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_chekout_q.id, ok=True)
#2
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=ClientState.TRY_TO_PAY_2)
async def successful_payment(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    payment_info = message.successful_payment.to_python()
    generate_qr(message.from_user.id, message.from_user.username, message.from_user.first_name,message.from_user.last_name, '1+1')
    insert_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, '1+1')
    photo = InputFile(f'qr_codes/'f'{message.from_user.id}_1+1.jpg')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    msg = '''Вы купили билет 1+1'''
    buy_ticket = KeyboardButton('Купить билет')
    info = KeyboardButton('О нас')
    prize = KeyboardButton('Розыгрыш от MOSPIT')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
    my_tickets = KeyboardButton('Мои билеты')
    markup.row(buy_ticket, info)
    markup.row(prize, otzyv)
    markup.row(my_tickets)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_ORDER)
@dp.message_handler(text=['Отмена'], state=ClientState.TRY_TO_PAY_3)
async def otmena(message : types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 3)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
        msg = '''Вы отменили платёж'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSHPIT')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup.row(buy_ticket, info)
        markup.row(prize, otzyv)
        markup.row(my_tickets)
        await message.answer(msg, reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
@dp.pre_checkout_query_handler(lambda query: True, state=ClientState.TRY_TO_PAY_3)
async def pre_checkout_query(pre_chekout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_chekout_q.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=ClientState.TRY_TO_PAY_3)
async def successful_payment(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    payment_info = message.successful_payment.to_python()
    generate_qr(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'vip')
    insert_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'vip')
    photo = InputFile(f'qr_codes/{message.from_user.id}_vip.jpg')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    msg = '''Вы купили билет на ранний вход'''
    buy_ticket = KeyboardButton('Купить билет')
    info = KeyboardButton('О нас')
    prize = KeyboardButton('Розыгрыш от MOSPIT')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
    my_tickets = KeyboardButton('Мои билеты')
    markup.row(buy_ticket, info)
    markup.row(prize, otzyv)
    markup.row(my_tickets)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_ORDER)
@dp.message_handler(text=['Отмена'], state=ClientState.TRY_TO_PAY_4)
async def otmena(message : types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 3)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
        msg = '''Вы отменили платёж'''
        buy_ticket = KeyboardButton('Купить билет')
        info = KeyboardButton('О нас')
        prize = KeyboardButton('Розыгрыш от MOSHPIT')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
        my_tickets = KeyboardButton('Мои билеты')
        markup.row(buy_ticket, info)
        markup.row(prize, otzyv)
        markup.row(my_tickets)
        await message.answer(msg, reply_markup=markup)
        await state.set_state(ClientState.START_ORDER)
@dp.pre_checkout_query_handler(lambda query: True, state=ClientState.TRY_TO_PAY_4)
async def pre_checkout_query(pre_chekout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_chekout_q.id, ok=True)

#4
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=ClientState.TRY_TO_PAY_4)
async def successful_payment(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    payment_info = message.successful_payment.to_python()
    generate_qr(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'premium')
    insert_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 'premium')
    photo = InputFile(f'qr_codes/{message.from_user.id}_premium.jpg')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    msg = '''Столик на 6 человек\nклассного вечера)'''
    buy_ticket = KeyboardButton('Купить билет')
    info = KeyboardButton('О нас')
    prize = KeyboardButton('Розыгрыш от MOSHPIT')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    otzyv = KeyboardButton('Отзывы о сервисе и MOSHPIT')
    my_tickets = KeyboardButton('Мои билеты')
    markup.row(buy_ticket, info)
    markup.row(prize, otzyv)
    markup.row(my_tickets)
    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.START_ORDER)
if __name__ == '__main__':
    executor.start_polling(dp)
