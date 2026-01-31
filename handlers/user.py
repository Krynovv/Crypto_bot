from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboard import direct_kb, kb, news_kb
from service.services import get_price_change


user_router = Router()


# Этот хэндлер срабатывает на команду /start
@user_router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU["/start"], reply_markup=kb)

@user_router.message(F.text == LEXICON_RU["button_direction"])
async def process_direct_answer(message:Message):
    await message.answer(text=LEXICON_RU["direct"], reply_markup=direct_kb)

@user_router.message(F.text == LEXICON_RU["button_news"])
async def process_news_answer(message:Message):
    await message.answer(text=LEXICON_RU["news"], reply_markup=news_kb)

@user_router.message(F.text == LEXICON_RU["button_news_BTC"])
async def process_news_BTC_answer(message:Message):
    news_BTC = get_price_change("bitcoin", days=1)
    await message.answer(news_BTC)

