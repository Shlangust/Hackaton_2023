from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton

role = ''
password=''
user_id=''
import pymysql
TOKEN = '6782881493:AAHs_h8oRFGK8z1fxNl6C_v-Do6DJouslhc'

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
    global user_id
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
        global role
        role = 'std'
        await callback.message.answer('Введите пароль')

        # Ожидание следующего сообщения (пароля) от пользователя
        @dp.message_handler(content_types=types.ContentType.TEXT)
        async def process_password(message: types.Message):
            global password
            password = message.text
            print(password)  # Печатает значение password в консоли

        dp.register_message_handler(process_password)


    @dp.callback_query_handler(text='1')
    async def teach_replue_1(callback: types.CallbackQuery):
        await callback.message.answer('Введите пароль')

        # Ожидание следующего сообщения (пароля) от пользователя
        @dp.message_handler(content_types=types.ContentType.TEXT)
        async def teach_password(message: types.Message):
            global password
            password = message.text
            print(password)  # Печатает значение password в консоли

        dp.register_message_handler(teach_password)
        global role
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
                global password
                password = message.text
                print(password)  # Печатает значение password в консоли

             dp.register_message_handler(adm_password)
            global role
            role = 'adm'

    async def insert_toDB(user_id,role,password):
     with connection.cursor() as cursor:
        insert_query = "INSERT INTO users (user, role, password) VALUES ('" + str(user_id) + "', '" + role + "', '" + password + "');"
        cursor.execute(insert_query)
        # connection.commit()
        select_all_rows = "SELECT * FROM users;"
        cursor.execute(select_all_rows)
        rows = cursor.fetchall()
        print(rows)

print(role,user_id,password)


if __name__ == '__main__':
    executor.start_polling(dp)
