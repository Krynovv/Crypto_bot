from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import requests
from config.config import config

bot = Bot(token=config.bot.token)
dp = Dispatcher()

#Комманда /start
async def process_start_command(message: Message):
   await message.answer('Привет. Данный бот делает предсказание для крипто валют.\n Предсказания, являются не рекомендацией и могут быть ошибочны!')

#Комманда /help
async def process_help_command(message: Message):
   await message.answer(command_help)
#текс help
command_help = '123131'

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# кроме команд "/start" и "/help"
@dp.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(
            text='Данный тип апдейтов не поддерживается '
                 'методом send_copy'
        )

dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_start_command, Command(commands='start'))

if __name__ == '__main__':
   dp.run_polling(bot)