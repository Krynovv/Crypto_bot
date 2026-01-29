import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.other import other_router
from handlers.user import user_router
from config.config import Config, load_config

#Инициализируем логгер
logger = logging.getLogger(__name__)

#Функция конфигурирования и запуска бота
async def main():
   # Загружаем конфиг в переменную
   config: Config = load_config()

   # Задаем базовую конфигурацию логирования
   logging.basicConfig(
      level=logging.getLevelName(level=config.log.level),
      format=config.log.format,
   )

   logger.info("Starting bot")

   # Инициализируем бота и диспетчер
   bot = Bot(
      token=config.bot.token,
      default=DefaultBotProperties(parse_mode=ParseMode.HTML),
   )
   dp = Dispatcher()

   dp.include_router(user_router)
   dp.include_router(other_router)

   await bot.delete_webhook(drop_pending_updates=True)
   await dp.start_polling(bot)

if __name__ == "__main__":
   asyncio.run(main())