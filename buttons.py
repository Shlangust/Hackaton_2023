from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton

TOKEN = '6782881493:AAHs_h8oRFGK8z1fxNl6C_v-Do6DJouslhc'

bot = Bot(TOKEN)
dp = Dispatcher(bot)

role = 'std'

bkb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
bb1 = KeyboardButton('Рассписание')
bb2 = KeyboardButton('помощь')
bkb.add(bb1,bb2)

@dp.message_handler(commands='start')
async def start_if_reg(message: types.message):
    await message.answer('с возвращением!',reply_markup=bkb)

@dp.message_handler()
async def button_check(message: types.message):
    if message.text == 'помощь':
        await message.answer('test1')
    if message.text == 'Рассписание':
        await  message.answer('введите группу')
          # if message.text in ОБРАЩЕНИЕ К БД
          #      await message.answer(ВЫВОД ПАР)


if __name__ == '__main__':
    executor.start_polling(dp)