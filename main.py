from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
# from reg import reg_main

import pymysql




TOKEN = '6425346422:AAHzlh_FO_ckMpm9dwZA8llyZCwIZvrh4VE'

bot = Bot(TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
b1 = KeyboardButton('Рассписание')
b2 = KeyboardButton('помощь')
kb.add(b1,b2)






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
async def start_comand(message: types.message):
    await message.answer('sfs')

@dp.message_handler()
async def help_button(message: types.Message):
    if message.text == 'помощь':
        await message.answer(text=help_in)
    if message.text == 'Рассписание':
        ikb = InlineKeyboardMarkup(row_width=2)
        ib1 = InlineKeyboardButton(text='Группа 1', callback_data='0')
        ib2 = InlineKeyboardButton(text='Группа 2', callback_data='1')
        ikb.add(ib1, ib2)
        await message.answer(text='выберите группу',reply_markup=ikb)

@dp.callback_query_handler(text='0')
async def schedule_replue_1(callback: types.CallbackQuery):
    await callback.message.edit_text('Рассписание группы 1')

@dp.callback_query_handler(text='1')
async def schedule_replue_2(callback: types.CallbackQuery):
    await callback.message.edit_text('Рассписание группцы 2')







if __name__ == '__main__':
    executor.start_polling(dp)