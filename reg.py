from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton

import pymysql
TOKEN = '6425346422:AAHzlh_FO_ckMpm9dwZA8llyZCwIZvrh4VE'

bot = Bot(TOKEN)
dp = Dispatcher(bot)


try:
    connection = pymysql.connect(
        host="localhost",
        port=3306,
        user="t_bot",
        password="admbot",
        database="educational_institution_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    print("успешное подключение к бд")
except Exception as ex:
    print("не получилось подключиться к бд, ошибка:", ex)


@dp.message_handler(commands=['start'])
async def reg(message: types.message):
    await message.answer('Зарегестрируйтесь')
    user_id = message.from_user.id
    print(user_id)
    if True:
     ikb = InlineKeyboardMarkup(row_width=2)
     ib1 = InlineKeyboardButton(text='Студент', callback_data='0')
     ib2 = InlineKeyboardButton(text='Преподователь', callback_data='1')
     ib3 = InlineKeyboardButton(text='Админ', callback_data='2')
     ikb.add(ib1, ib2,ib3)
     await message.answer(text='выберете роль',reply_markup=ikb)

    @dp.callback_query_handler(text='0')
    async def std_replue(callback: types.CallbackQuery):
        await callback.message.answer('Введите пароль')

        # Ожидание следующего сообщения (пароля) от пользователя
        @dp.message_handler(content_types=types.ContentType.TEXT)
        async def process_password(message: types.Message):
            password = message.text
            print(password)  # Печатает значение password в консоли

        dp.register_message_handler(process_password)

        role = 'std'

    @dp.callback_query_handler(text='1')
    async def teach_replue_1(callback: types.CallbackQuery):
        await callback.message.answer('Введите пароль')

        # Ожидание следующего сообщения (пароля) от пользователя
        @dp.message_handler(content_types=types.ContentType.TEXT)
        async def teach_password(message: types.Message):
            password = message.text
            print(password)  # Печатает значение password в консоли

        dp.register_message_handler(teach_password)

        role = 'teach'

    @dp.callback_query_handler(text='2')
    async def adm_replue_1(callback: types.CallbackQuery):
        await callback.message.answer('Введите админ  пароль')

        @dp.message_handler(content_types=types.ContentType.TEXT)
        async def adm_check_password(message: types.Message):
            if message.text == '123':
             await callback.message.answer('Введите пароль')

             @dp.message_handler(content_types=types.ContentType.TEXT)
             async def adm_password(message: types.Message):
                password = message.text
                print(password)  # Печатает значение password в консоли

             dp.register_message_handler(adm_password)

            role = 'adm'










if __name__ == '__main__':
    executor.start_polling(dp)
