from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import requests
from config.config import config

bot = Bot(token=config.bot.token)
dp = Dispatcher()

if __name__ == '__main__':
   dp.run_polling(bot)