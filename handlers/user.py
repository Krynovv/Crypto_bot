from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboard import direct_kb, kb, news_kb
from service.services import get_price_change


user_router = Router()


# хэндлер срабатывает на команду /start
@user_router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU["/start"], reply_markup=kb)

# хэндлер срабатывает на кнопку назад
@user_router.message(F.text == LEXICON_RU["button_return"])
async def process_return_answer(message:Message):
    await message.answer(text=LEXICON_RU["main_menu"], reply_markup = kb)
    await message.delete()

@user_router.message(F.text == LEXICON_RU["button_direction"])
async def process_direct_answer(message:Message):
    await message.answer(text=LEXICON_RU["direct"], reply_markup=direct_kb)

@user_router.message(F.text == LEXICON_RU["button_news"])
async def process_news_answer(message:Message):
    await message.answer(text= LEXICON_RU["news"], reply_markup=news_kb)

@user_router.message(
    F.text.in_([LEXICON_RU["button_news_BTC"], LEXICON_RU["button_news_ETH"], LEXICON_RU["button_news_BNB"], LEXICON_RU["button_news_SOL"] ])
)

async def process_news_coin_answer(message:Message):
    coin_map = {
        LEXICON_RU["button_news_BTC"]: "bitcoin",
        LEXICON_RU["button_news_ETH"]: "ethereum",
        LEXICON_RU["button_news_BNB"]: "binancecoin",
        LEXICON_RU["button_news_SOL"]: "solana"
    }
    coin_choise = coin_map.get(message.text)
    news_text = get_price_change(coin_choise, days=1)
    await message.answer(news_text)
    await message.delete()


