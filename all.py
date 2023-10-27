from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import numpy as np
import pymysql
from datetime import datetime


TOKEN = '6800392990:AAHQ_r3FqOOav12YBSb9gdA5XjSo6G77XOM'

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)

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


class Form(StatesGroup):
    sname = State()
    ssurname = State()
    spname = State()
    sgp = State()
    keypass = State()
    nokeypass = State()
    registred = State()
    rasp = State()
    rasuch = State()
    pred = State()
    den = State()
    grupp = State()
    inform = State()

dn, text = '', ''
role = ''
password = ''
user_id = ''
c = 0
pswrd = ''
name, surname, pname, gp = '', '', '', ''
canReg = True

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


help_in = '''
/help - помощь по боту
/discription - описание функционала и назначение бота
'''

discription_in = '''
этот бот являеется проектом для хакатона в РКСИ

'''
@dp.message_handler(commands=['discription'])
async def discription_comand(message: types.message):
    await message.answer(discription_in)



@dp.message_handler(commands=['help'])
async def help_comand(message: types.message):
    await message.answer(help_in)

@dp.message_handler(commands=['start'])
async def start_comand(message: types.message, state:FSMContext):
    global role, user_id
    user_id = message.from_user.id
    with connection.cursor() as cursor:
        cursor.execute("SELECT uid FROM users;")
        rows = cursor.fetchall()
        rows = np.array(rows)
        if user_id in rows:
            cursor.execute("SELECT role FROM users;")
            role = cursor.fetchall()
            role = np.array(role)
            role = role[np.where(rows == user_id)]
            role = role[0]
        else:
            role = ' '
    if role == ' ':
        await message.answer('Ваш id ещё не зарегестрирован')
        await message.answer('Регистрация')
        global canReg
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
                else:
                    await callback.message.answer('вы ввели пароль неверно, ещё попытка')

            if canReg:
                await callback.message.answer(
                    'Аккаунт студента\nВы будете зарегестрированы по telegram id, придумайте и '
                    'введите пароль')
                dp.register_message_handler(student_password)
            else:
                await message.answer(text='вы уже зарегестрированы')

            @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sname)
            async def student_n4(message: types.Message):
                global name
                name = message.text
                await callback.message.answer('ваша фамилия?')
                await state.set_state(Form.ssurname)

            @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.ssurname)
            async def student_n3(message: types.Message):
                global surname
                surname = message.text
                await callback.message.answer('ваше отчество?')
                await state.set_state(Form.spname)

            @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.spname)
            async def student_n2(message: types.Message):
                global pname
                pname = message.text
                await callback.message.answer('в какой группе вы учитесь?')
                await state.set_state(Form.sgp)

            @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.sgp)
            async def student_n(message: types.Message):
                global pname, name, surname, gp
                gp = message.text
                insert_to_uinfo(user_id, gp, name, surname, pname)
                await callback.message.answer('Регистрация окончена. Хорошей учёбы!')
                bkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                bb1 = KeyboardButton('Расписание')
                bb2 = KeyboardButton('дз')
                bb3 = KeyboardButton('Доп. Информация')
                bkb.add(bb1, bb2, bb3)
                await message.answer('теперь можете начинать работу', reply_markup=bkb)
                await state.set_state(Form.registred)

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
                bkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                bb1 = KeyboardButton('Расписание')
                bb2 = KeyboardButton('Домашнее задание')
                bb3 = KeyboardButton('Доп. Информация')
                bkb.add(bb1, bb2, bb3)
                await message.answer('теперь можете начинать работу', reply_markup=bkb)
                await state.set_state(Form.registred)

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
                await state.set_state(Form.registred)
    elif role == 'std':
        bkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bb1 = KeyboardButton('Расписание')
        bb2 = KeyboardButton('дз')
        bb3 = KeyboardButton('Доп. Информация')
        bkb.add(bb1, bb2, bb3)
        await message.answer('теперь можете начинать работу', reply_markup=bkb)
        with connection.cursor() as cursor:
            user_id = message.from_user.id
            cursor.execute("SELECT uid FROM uinfo;")
            crows = cursor.fetchall()
            crows = np.array(crows)
            cursor.execute("SELECT gp FROM uinfo;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            gr = [np.where(crows == user_id)]
            gr = rows[gr[0][0][0]][0]
            cursor.execute("SELECT gp FROM lchange;")
            crows = cursor.fetchall()
            crows = np.array(crows)
            if (gr in rows) or (gr in crows):
                cnpar = [np.where(crows == gr)]
                cursor.execute("SELECT * FROM lchange;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                viv = ''
                prs = []
                now = str(datetime.now())
                year = int(now[0:4])
                day = int(now[8:10])
                month = int(now[5:7])
                for i in range(len(cnpar[0][0])):
                    date = str(crows[cnpar[0][0][i]][0])
                    if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                        st = ''
                        st += str(crows[cnpar[0][0][i]][1]) + '. изм.  ' + str(crows[cnpar[0][0][i]][2]) + '\n'
                        st += 'уч. ' + str(crows[cnpar[0][0][i]][3]) + '; каб. ' + str(crows[cnpar[0][0][i]][5]) + '\n'
                        print(st)
                        prs.append(st)
                viv += 'Пары сегодня\n'
                prs = np.array(prs)
                prs.sort()
                for ii in range(len(prs)):
                    viv += prs[ii]
                try:
                    exmpl = prs[0]
                except:
                    viv += "нет\n"
                viv += '\n'
                await message.answer(viv)
            else:
                viv = 'сегодня изменений пар нет'
        await message.answer(viv)
        await state.set_state(Form.registred)
    elif role == 'tch': pass

@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.registred)
async def button_check(message: types.message, state:FSMContext):
    global role, gr
    if message.text == 'Домашнее задание' and role == 'tch':
        with connection.cursor() as cursor:
            user_id = message.from_user.id
            cursor.execute("SELECT uid FROM uinfo;")
            crows = cursor.fetchall()
            crows = np.array(crows)
            cursor.execute("SELECT surname FROM uinfo;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            gr = [np.where(crows == user_id)]
            gr = rows[gr[0][0][0]][0]
            cursor.execute("SELECT name FROM uinfo;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            g = [np.where(crows == user_id)]
            g = rows[g[0][0][0]][0]
            gr += ' ' + g[0] + '.'
            cursor.execute("SELECT pname FROM uinfo;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            g = [np.where(crows == user_id)]
            g = rows[g[0][0][0]][0]
            gr += ' ' + g[0] + '.'
        await message.answer(text='Создание домашнего задания')
        await message.answer(text='Какой предмет?')
        await state.set_state(Form.pred)

    elif message.text == 'дз':
        pass
    elif message.text == 'Расписание':
        rikb = InlineKeyboardMarkup(row_width=2)
        rib1 = InlineKeyboardButton(text='Расписание пар', callback_data='rpar')
        rib2 = InlineKeyboardButton(text='Расписание преподователей', callback_data='rprep')
        rib3 = InlineKeyboardButton(text='Мои пары', callback_data='myr')
        rikb.add(rib1, rib2, rib3)
        await message.answer(text='выберете расписание', reply_markup=rikb)
    elif message.text == 'Доп. Информация':
        rikb = InlineKeyboardMarkup(row_width=2)
        rib1 = InlineKeyboardButton(text='Административные отделения', callback_data='d0')
        rib2 = InlineKeyboardButton(text='Материалы по предметам', callback_data='d1')
        rib3 = InlineKeyboardButton(text='Учебный план', callback_data='d2')
        rib4 = InlineKeyboardButton(text='Образцы документов', callback_data='d3')
        rikb.add(rib1, rib2, rib3, rib4)
        await message.answer(text='что вы хотите?', reply_markup=rikb)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.pred)
    async def std_r2(callback: types.CallbackQuery):
        global pname
        pname = message.text
        await message.answer(text='На какой день?\n(формат дд.мм.гггг)')
        await state.set_state(Form.den)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.den)
    async def std_r3(callback: types.CallbackQuery):
        global dn
        dn = message.text
        await message.answer(text='Для какой группы?')
        await state.set_state(Form.grupp)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.grupp)
    async def std_r4(callback: types.CallbackQuery):
        global gp
        gp = message.text
        await message.answer(text='Теперь введите основную информацию о домашнем задании\n(у вас 1024 символа)')
        await state.set_state(Form.inform)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.inform)
    async def std_r4(callback: types.CallbackQuery):
        global text, gr, dn, pname, gp
        text = message.text
        await message.answer(text='Домашнее задание внесено')
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO uinfo (date, lname, teacher, gp, inf) VALUES ('" + dn + "', '" + pname + "', '" + gr + "', '" + gp + "', '" + text + "');"
            cursor.execute(insert_query)
            connection.commit()           # раскоментить в финальной версии
        await state.set_state(Form.registred)

    @dp.callback_query_handler(text='d3', state=Form.registred)
    async def std_r2(callback: types.CallbackQuery):
        await message.reply_document(open('docs\\d.py', 'rb'))

    @dp.callback_query_handler(text='rpar', state=Form.registred)
    async def std_r1(callback: types.CallbackQuery):
        await message.answer('для какой группы?')
        await state.set_state(Form.rasp)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.rasp)
    async def student_name(message: types.Message):
        global c
        gr = message.text
        with connection.cursor() as cursor:
            cursor.execute("SELECT gp FROM lessons;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            cursor.execute("SELECT gp FROM lchange;")
            crows = cursor.fetchall()
            crows = np.array(crows)
            if (gr in rows) or (gr in crows):
                npar = [np.where(rows == gr)]
                cnpar = [np.where(crows == gr)]
                cursor.execute("SELECT * FROM lessons;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                cursor.execute("SELECT * FROM lchange;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                c = 0
                viv = ''
                prs = []
                now = str(datetime.now())
                year = int(now[0:4])
                day = int(now[8:10])
                month = int(now[5:7])
                for iii in range(7):
                    for i in range(len(cnpar[0][0])):
                        date = str(crows[cnpar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(crows[cnpar[0][0][i]][1]) + '. изменение: ' + str(
                                crows[cnpar[0][0][i]][2]) + '\n'
                            st += 'уч. ' + str(crows[cnpar[0][0][i]][3]) + '; каб. ' + str(
                                    crows[cnpar[0][0][i]][5]) + '\n'
                            prs.append(st)
                    for i in range(len(npar[0][0])):
                        date = str(rows[npar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(rows[npar[0][0][i]][1]) + '. ' + str(rows[npar[0][0][i]][2]) + '\n'
                            st += 'уч. ' + str(rows[npar[0][0][i]][3]) + '; каб. ' + str(
                                rows[npar[0][0][i]][5]) + '\n'
                            prs.append(st)
                    viv += 'Пары на ' + str(day) + "." + str(month) + "." + str(year) + '\n'
                    prs = np.array(prs)
                    prs.sort()
                    for ii in range(len(prs)):
                        viv += prs[ii]
                    try:
                        exmpl = prs[0]
                    except:
                        viv += "нет\n"
                    prs = []
                    viv += '\n'

                    day += 1
                    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                        if day == 32:
                            day = 1
                            month += 1
                            if month == 13:
                                month = 1
                                year += 1
                    elif month == 4 or month == 6 or month == 9 or month == 11:
                        if day == 31:
                            day = 1
                            month += 1
                    else:
                        if day == 29:
                            day = 1
                            month += 1
                await message.answer(viv)

            else:
                await message.answer('для этой группы пар нет\nможно отдыхать\n(если только правильно ввели группу)')
            await state.set_state(Form.registred)

    @dp.callback_query_handler(text='myr', state=Form.registred)
    async def std_r2(callback: types.CallbackQuery):
        global role
        if role == 'std':
            with connection.cursor() as cursor:
                user_id = message.from_user.id
                cursor.execute("SELECT uid FROM uinfo;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                cursor.execute("SELECT gp FROM uinfo;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                gr = [np.where(crows == user_id)]
                gr = rows[gr[0][0][0]][0]
                cursor.execute("SELECT gp FROM lessons;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                cursor.execute("SELECT gp FROM lchange;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                if (gr in rows) or (gr in crows):
                    npar = [np.where(rows == gr)]
                    cnpar = [np.where(crows == gr)]
                    cursor.execute("SELECT * FROM lessons;")
                    rows = cursor.fetchall()
                    rows = np.array(rows)
                    cursor.execute("SELECT * FROM lchange;")
                    crows = cursor.fetchall()
                    crows = np.array(crows)
                    viv = ''
                    prs = []
                    now = str(datetime.now())
                    year = int(now[0:4])
                    day = int(now[8:10])
                    month = int(now[5:7])
                    for i in range(len(cnpar[0][0])):
                        date = str(crows[cnpar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(crows[cnpar[0][0][i]][1]) + '. изм.  ' + str(crows[cnpar[0][0][i]][2]) + '\n'
                            st += 'уч. ' + str(crows[cnpar[0][0][i]][3]) + '; каб. ' + str(crows[cnpar[0][0][i]][5]) + '\n'
                            print(st)
                            prs.append(st)
                    for i in range(len(npar[0][0])):
                        date = str(rows[npar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(rows[npar[0][0][i]][1]) + '. ' + str(rows[npar[0][0][i]][2]) + '\n'
                            st += 'уч. ' + str(rows[npar[0][0][i]][3]) + '; каб. ' + str(rows[npar[0][0][i]][5]) + '\n'
                            prs.append(st)
                    viv += 'Пары сегодня\n'
                    prs = np.array(prs)
                    prs.sort()
                    for ii in range(len(prs)):
                        viv += prs[ii]
                    try:
                        exmpl = prs[0]
                    except:
                        viv += "нет\n"
                    viv += '\n'
                    await message.answer(viv)
        elif role == 'tch':
            with connection.cursor() as cursor:
                user_id = message.from_user.id
                cursor.execute("SELECT uid FROM uinfo;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                cursor.execute("SELECT surname FROM uinfo;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                gr = [np.where(crows == user_id)]
                gr = rows[gr[0][0][0]][0]
                cursor.execute("SELECT name FROM uinfo;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                g = [np.where(crows == user_id)]
                g = rows[g[0][0][0]][0]
                gr += ' ' + g[0] + '.'
                cursor.execute("SELECT pname FROM uinfo;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                g = [np.where(crows == user_id)]
                g = rows[g[0][0][0]][0]
                gr += ' ' + g[0] + '.'
                cursor.execute("SELECT teacher FROM lessons;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                cursor.execute("SELECT teacher FROM lchange;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                if (gr in rows) or (gr in crows):
                    npar = [np.where(rows == gr)]
                    cnpar = [np.where(crows == gr)]
                    cursor.execute("SELECT * FROM lessons;")
                    rows = cursor.fetchall()
                    rows = np.array(rows)
                    cursor.execute("SELECT * FROM lchange;")
                    crows = cursor.fetchall()
                    crows = np.array(crows)
                    viv = ''
                    prs = []
                    now = str(datetime.now())
                    year = int(now[0:4])
                    day = int(now[8:10])
                    month = int(now[5:7])
                    for i in range(len(cnpar[0][0])):
                        date = str(crows[cnpar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(crows[cnpar[0][0][i]][1]) + '. изм.  ' + str(crows[cnpar[0][0][i]][2]) + '\n'
                            st += 'группа ' + str(crows[cnpar[0][0][i]][4]) + '; каб. ' + str(crows[cnpar[0][0][i]][5]) + '\n'
                            print(st)
                            prs.append(st)
                    for i in range(len(npar[0][0])):
                        date = str(rows[npar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(rows[npar[0][0][i]][1]) + '. ' + str(rows[npar[0][0][i]][2]) + '\n'
                            st += 'группа ' + str(rows[npar[0][0][i]][4]) + '; каб. ' + str(rows[npar[0][0][i]][5]) + '\n'
                            prs.append(st)
                    viv += 'Пары сегодня\n'
                    prs = np.array(prs)
                    prs.sort()
                    for ii in range(len(prs)):
                        viv += prs[ii]
                    try:
                        exmpl = prs[0]
                    except:
                        viv += "нет\n"
                    viv += '\n'
                    await message.answer(viv)

    @dp.callback_query_handler(text='rprep', state=Form.registred)
    async def std_r3(callback: types.CallbackQuery):
        await message.answer('преподаватель?\nв формате "Фамилия И. О."')
        await state.set_state(Form.rasuch)

    @dp.message_handler(content_types=types.ContentType.TEXT, state=Form.rasuch)
    async def prep_name(message: types.Message):
        global c
        gr = message.text
        with connection.cursor() as cursor:
            cursor.execute("SELECT teacher FROM lessons;")
            rows = cursor.fetchall()
            rows = np.array(rows)
            cursor.execute("SELECT teacher FROM lchange;")
            crows = cursor.fetchall()
            crows = np.array(crows)
            if (gr in rows) or (gr in crows):
                npar = [np.where(rows == gr)]
                cnpar = [np.where(crows == gr)]
                cursor.execute("SELECT * FROM lessons;")
                rows = cursor.fetchall()
                rows = np.array(rows)
                cursor.execute("SELECT * FROM lchange;")
                crows = cursor.fetchall()
                crows = np.array(crows)
                c = 0
                viv = ''
                prs = []
                now = str(datetime.now())
                year = int(now[0:4])
                day = int(now[8:10])
                month = int(now[5:7])
                for iii in range(7):
                    for i in range(len(cnpar[0][0])):
                        date = str(crows[cnpar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(crows[cnpar[0][0][i]][1]) + '. изменено: ' + str(
                                crows[cnpar[0][0][i]][2]) + '\n'
                            st += str(crows[cnpar[0][0][i]][3]) + '; каб. ' + str(crows[cnpar[0][0][i]][5]) + '\n'
                            st += crows[cnpar[0][0][i]][4] + '\n'
                            prs.append(st)
                    for i in range(len(npar[0][0])):
                        date = str(rows[npar[0][0][i]][0])
                        if (int(date[6:]) == year) and (int(date[0:2]) == day) and (int(date[3:5]) == month):
                            st = ''
                            st += str(rows[npar[0][0][i]][1]) + '. ' + str(rows[npar[0][0][i]][2]) + '\n'
                            st += str(rows[npar[0][0][i]][3]) + '; каб. ' + str(
                                rows[npar[0][0][i]][5]) + '\n'
                            st += rows[npar[0][0][i]][4] + '\n'
                            prs.append(st)
                    viv += 'Пары на ' + str(day) + "." + str(month) + "." + str(year) + '\n'
                    prs = np.array(prs)
                    prs.sort()
                    for ii in range(len(prs)):
                        viv += prs[ii]
                    try:
                        exmpl = prs[0]
                    except:
                        viv += "нет\n"
                    prs = []
                    viv += '\n'

                    day += 1
                    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                        if day == 32:
                            day = 1
                            month += 1
                            if month == 13:
                                month = 1
                                year += 1
                    elif month == 4 or month == 6 or month == 9 or month == 11:
                        if day == 31:
                            day = 1
                            month += 1
                    else:
                        if day == 29:
                            day = 1
                            month += 1
                await message.answer(viv)

            else:
                await message.answer('у этого преподавателя нет пар\n(убедитесь, что правильно написали)')
            await state.set_state(Form.registred)





if __name__ == '__main__':
    executor.start_polling(dp)