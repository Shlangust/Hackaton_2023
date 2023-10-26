from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import pymysql


class Form(StatesGroup):
    sname = State()
    ssurname = State()
    spname = State()
    sgp = State()
    keypass = State()
    nokeypass = State()

storage = MemoryStorage()

TOKEN = '6800392990:AAHQ_r3FqOOav12YBSb9gdA5XjSo6G77XOM'

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
canReg = True

try:
    connection = pymysql.connect(
        host="localhost",
        port=3306,
        user="t_bot",
        password="admbot",
        database="educational_institution_db",
    )
except Exception as ex:
    print("ошибка:", ex)

role = ''
password = ''
user_id = ''
c = 0
pswrd = ''
name, surname, pname, gp = '', '', '', ''

def insert_to_db(ui, re, pw):
    with connection.cursor() as cursor:
        insert_query = "INSERT INTO users (uid, role, password) VALUES ('" + str(ui) + "', '" + re + "', '" + pw + "');"
        cursor.execute(insert_query)
        # connection.commit()           # раскоментить в финальной версии

def insert_to_uinfo(ui, g, n, s, p):
    with connection.cursor() as cursor:
        insert_query = "INSERT INTO uinfo (uid, gp, name, surname, pname) VALUES ('" + str(ui) + "', '" + g + "', '" + n + "', '" + s + "', '" + p + "');"
        cursor.execute(insert_query)
        # connection.commit()           # раскоментить в финальной версии


@dp.message_handler(commands=['start'])
async def reg(message: types.message, state:FSMContext):
    await message.answer('Регистрация')
    global user_id, canReg
    user_id = message.from_user.id
    with connection.cursor() as cursor:
        cursor.execute("SELECT uid FROM users;")
        rows = cursor.fetchall()
    if (user_id not in rows) and canReg:
        ikb = InlineKeyboardMarkup(row_width=1)
        ib1 = InlineKeyboardButton(text='Студент', callback_data='0')
        ib2 = InlineKeyboardButton(text='Преподаватель', callback_data='1')
        ib3 = InlineKeyboardButton(text='Администратор', callback_data='2')
        ikb.add(ib1, ib2, ib3)
        await message.answer(text='ваша роль?', reply_markup=ikb)
    else:
        await message.answer(text='вы уже зарегестрированы')

    @dp.callback_query_handler(text='0')
    async def std_replue(callback: types.CallbackQuery):
        await state.set_state(Form.nokeypass)
        global role, canReg, c
        role = 'std'
        c = 0

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.nokeypass)
        async def student_password(message: types.Message):
            global password, canReg, role, c, pswrd
            password = message.text
            await message.delete()
            if c == 0:
                pswrd = password
                await callback.message.answer('подтвердите пароль повторным вводом')
                c += 1
            elif password == pswrd:
                insert_to_db(user_id, role, password)
                canReg = False
                await callback.message.answer('не забудьте пароль!')
                await callback.message.answer('теперь немного о вас...')
                await callback.message.answer('как вас зовут?')
                await state.set_state(Form.sname)
                dp.register_message_handler(student_name)
            else:
                await callback.message.answer('вы ввели пароль неверно, ещё попытка')

        if canReg:
            await callback.message.answer('Аккаунт студента\nВы будете зарегестрированы по telegram id, придумайте и '
                                          'введите пароль')
            dp.register_message_handler(student_password)
        else:
            await message.answer(text='вы уже зарегестрированы')

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sname)
        async def student_name(message: types.Message):
            global name
            name = message.text
            await callback.message.answer('ваша фамилия?')
            await state.set_state(Form.ssurname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.ssurname)
        async def student_name(message: types.Message):
            global surname
            surname = message.text
            await callback.message.answer('ваше отчество?')
            await state.set_state(Form.spname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.spname)
        async def student_name(message: types.Message):
            global pname
            pname = message.text
            await callback.message.answer('в какой группе вы учитесь?')
            await state.set_state(Form.sgp)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sgp)
        async def student_name(message: types.Message):
            global pname, name, surname, gp
            gp = message.text
            insert_to_uinfo(user_id, gp, name, surname, pname)
            await callback.message.answer('Регистрация окончена. Хорошей учёбы!')



    @dp.callback_query_handler(text='1')
    async def teach_replue_1(callback: types.CallbackQuery):
        await callback.message.answer(
            'Для регистрации учителя вам необходим специальный код. Если он у вас уже есть, введите')
        await state.set_state(Form.nokeypass)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.nokeypass)
        async def tch_check_password(message: types.Message):
            global canReg, c
            if (message.text == '123') and canReg:
                await message.delete()
                global role
                role = 'tch'
                await callback.message.answer(
                    'Правильный код\nВы будете зарегестрированы по telegram id, придумайте и введите пароль')
                dp.register_message_handler(tch_password)
                c = 0
                await state.set_state(Form.keypass)
            elif canReg == False:
                await callback.message.answer('вы уже зарегестрированы')
            else:
                await callback.message.answer('неправильный код\nвведите повторно')

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.keypass)
        async def tch_password(message: types.Message):
            global password, canReg, role, c, pswrd
            password = message.text
            await message.delete()
            if c == 0:
                pswrd = password
                await callback.message.answer('подтвердите пароль повторным вводом')
                c += 1
            elif password == pswrd:
                insert_to_db(user_id, role, password)
                canReg = False
                await callback.message.answer('не забудьте пароль!')
                await callback.message.answer('теперь немного о вас...')
                await callback.message.answer('как вас зовут?')
                await state.set_state(Form.sname)
            else:
                await callback.message.answer('вы ввели пароль неверно, ещё попытка')

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sname)
        async def student_name(message: types.Message):
            global name
            name = message.text
            await callback.message.answer('ваша фамилия?')
            await state.set_state(Form.ssurname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.ssurname)
        async def student_name(message: types.Message):
            global surname
            surname = message.text
            await callback.message.answer('ваше отчество?')
            await state.set_state(Form.spname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.spname)
        async def student_name(message: types.Message):
            global pname, name, surname
            pname = message.text
            insert_to_uinfo(user_id, 'tch', name, surname, pname)
            await callback.message.answer('Регистрация окончена. Удачи в работе!')

    @dp.callback_query_handler(text='2')
    async def adm_replue_1(callback: types.CallbackQuery):
        await callback.message.answer(
            'Для регистрации администратора вам необходим специальный код. Если он у вас уже есть, введите')
        await state.set_state(Form.nokeypass)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.nokeypass)
        async def adm_check_password(message: types.Message):
            global canReg, c
            if (message.text == '123') and canReg:
                await message.delete()
                global role
                role = 'adm'
                await callback.message.answer(
                    'Правильный код\nВы будете зарегестрированы по telegram id, придумайте и введите пароль')
                dp.register_message_handler(adm_password)
                c = 0
                await state.set_state(Form.keypass)
            elif canReg == False:
                await callback.message.answer('вы уже зарегестрированы')
            else:
                await callback.message.answer('неправильный код\nвведите повторно')

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.keypass)
        async def adm_password(message: types.Message):
            global password, canReg, role, c, pswrd
            password = message.text
            await message.delete()
            if c == 0:
                pswrd = password
                await callback.message.answer('подтвердите пароль повторным вводом')
                c += 1
            elif password == pswrd:
                insert_to_db(user_id, role, password)
                canReg = False
                await callback.message.answer('не забудьте пароль!')
                await callback.message.answer('теперь немного о вас...')
                await callback.message.answer('как вас зовут?')
                await state.set_state(Form.sname)
            else:
                await callback.message.answer('вы ввели пароль неверно, ещё попытка')

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sname)
        async def student_name(message: types.Message):
            global name
            name = message.text
            await callback.message.answer('ваша фамилия?')
            await state.set_state(Form.ssurname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.ssurname)
        async def student_name(message: types.Message):
            global surname
            surname = message.text
            await callback.message.answer('ваше отчество?')
            await state.set_state(Form.spname)

        @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.spname)
        async def student_name(message: types.Message):
            global pname, name, surname
            pname = message.text
            insert_to_uinfo(user_id, 'adm', name, surname, pname)
            await callback.message.answer('Регистрация окончена. Удачи в работе!')


if __name__ == '__main__':
    executor.start_polling(dp)
