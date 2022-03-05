from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, CallbackQuery
from aiogram_calendar import SimpleCalendar, simple_cal_callback
import sqlite3
from CalendarApi import GoogleCalendar
from config import tg_bot_token
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

start_kb = ReplyKeyboardMarkup(resize_keyboard=True, )


def insert_client_to_db(name: str, date: int):
    """
    base for all users
    """
    sqlite_connection = sqlite3.connect('DBforTG.sqlite')
    cursor = sqlite_connection.cursor()
    info = cursor.execute('SELECT * FROM clients WHERE name=?', (name,))
    if info.fetchone() is None:
        cursor.execute('INSERT INTO clients (name, date) VALUES (?, ?)', (name, date))
        print('Запись сделана', cursor.rowcount)
        sqlite_connection.commit()
    else:
        print("Такой пользователь уже существует")
    cursor.close()


@dp.message_handler(Text(equals='Кто записался'))
async def get_info(message: types.Message):
    obj = GoogleCalendar()
    result = obj.get_events_list()
    for i in range(0, len(result)):
        name = result[i][0]
        date = result[i][1][:16].replace('T', ', ')
        await message.answer(f'@{name}, {date}')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Обо мне', 'Прайс', 'Запись на урок']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Привет! Ниже кнопки для быстрой навигации', reply_markup=keyboard)


@dp.message_handler(Text(equals='Прайс'))
async def get_price(message: types.Message):
    await message.answer('Секундочку...')
    await message.answer('1. Пробный урок 800р.\n'
                         '2. Один урок 2000р.\n'
                         '3. Сертификат на 4 занятия 7600р.\n'
                         '4. Сертификат на 8 занятий 14400р.\n'
                         '5. Сертификат на 16 занятий 26.400р.\n'
                         '\n'
                         'Выезд к Вам на дом - все вышеперечисленное удваивается:\n'
                         'Один урок 4000р.\n'
                         'Сертификат на 4 занятия 15200р.\n'
                         'Сертификат на 4 занятия 28800.\n'
                         'Сертификат на 4 занятия 52800.\n')


@dp.message_handler(Text(equals='Обо мне'))
async def get_about(message: types.Message):
    await message.answer('Меня зовут Элина!\n'
                         '•Со мной ты научишься играть на 🎹 и исполнишь свою мечту!\n'
                         '•Играю в ресторанах и на мероприятиях🔥')


@dp.message_handler(Text(equals='Запись на урок'))
async def get_calendar(message: types.Message):
    await message.answer('Ты можешь выбрать дату когда тебе удобно!\n'
                         'А далее, я с тобой свяжусь!')
    await message.reply('Держи!', reply_markup=start_kb)
    await message.answer("Выбирайте дату: ", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    try:
        selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
        if selected:
            await callback_query.message.answer(
                f'Вы выбрали: {date.strftime("%d/%m/%Y")}\n'
                f'Я с вами свяжусь в ближайшее время ☺️\n'
                f'Если нужна информация\n'
                f'Жмакай /start',
                reply_markup=start_kb
            )

            user_id = callback_query.from_user.username
            await bot.send_message(541893004, f'Господин @{user_id} хочет записаться на {date.strftime("%d/%m/%Y")}!')
            insert_client_to_db(user_id, date)

            obj = GoogleCalendar()
            event = obj.create_event_dict(user_id, callback_data['year'], callback_data['month'], callback_data['day'])
            obj.create_event(event)

    except sqlite3.Error as error:
        print('Ошибка', error)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('Я только для того чтобы выдать краткую информацию 😅\n'
                         'Жмакай /start')


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
