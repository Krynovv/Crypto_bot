from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboard import direct_kb, kb, news_kb
from service.services import get_price_change, CryptoPredictor


user_router = Router()

# Хранилище message_id для удаления
# {user_id: [message_id1, message_id2, ...]}
user_messages = {}


# Инициализация предиктора при импорте
predictor = CryptoPredictor(
    model_path="Model/best_models/lstm_improved.pth",
    scaler_path="DATA/scaler.pkl"
)


def add_user_message(user_id: int, message_id: int):
    """Сохраняем message_id пользователя"""
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message_id)


async def clear_user_messages(message: Message, keep_last: bool = False):
    """Удаляем все сообщения бота для пользователя"""
    user_id = message.from_user.id
    if user_id in user_messages:
        msg_ids = user_messages[user_id]
        if keep_last and msg_ids:
            # Оставляем последнее сообщение
            msg_ids = msg_ids[:-1]

        for msg_id in msg_ids:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass  # Игнорируем ошибки удаления

        if keep_last:
            user_messages[user_id] = [user_messages[user_id][-1]]
        else:
            user_messages[user_id] = []


# хэндлер срабатывает на команду /start
@user_router.message(CommandStart())
async def process_start_command(message: Message):
    await clear_user_messages(message)
    msg = await message.answer(text=LEXICON_RU["/start"], reply_markup=kb)
    add_user_message(message.from_user.id, msg.message_id)

# хэндлер срабатывает на кнопку назад
@user_router.message(F.text == LEXICON_RU["button_return"])
async def process_return_answer(message:Message):
    await clear_user_messages(message, keep_last=True)
    msg = await message.answer(text=LEXICON_RU["main_menu"], reply_markup = kb)
    add_user_message(message.from_user.id, msg.message_id)
    await message.delete()

@user_router.message(F.text == LEXICON_RU["button_direction"])
async def process_direct_answer(message:Message):
    await clear_user_messages(message, keep_last=True)
    msg = await message.answer(text=LEXICON_RU["direct"], reply_markup=direct_kb)
    add_user_message(message.from_user.id, msg.message_id)
    await message.delete()

@user_router.message(F.text == LEXICON_RU["button_news"])
async def process_news_answer(message:Message):
    await clear_user_messages(message, keep_last=True)
    msg = await message.answer(text= LEXICON_RU["news"], reply_markup=news_kb)
    add_user_message(message.from_user.id, msg.message_id)
    await message.delete()

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
    await clear_user_messages(message, keep_last=True)
    msg = await message.answer(news_text)
    add_user_message(message.from_user.id, msg.message_id)
    await message.delete()

# Хэндлеры для прогноза (кнопки BTC и ETH в меню Прогноз)
@user_router.message(F.text.in_([LEXICON_RU["button_BTC"], LEXICON_RU["button_ETH"], LEXICON_RU["button_SOL"], LEXICON_RU["button_BNB"]]))
async def process_forecast_answer(message: Message):
    coin_map = {
        LEXICON_RU["button_BTC"]: "bitcoin",
        LEXICON_RU["button_ETH"]: "ethereum",
        LEXICON_RU["button_SOL"]: "solana",
        LEXICON_RU["button_BNB"]: "binancecoin"
    }
    coin_choice = coin_map.get(message.text)

    # Удаляем старые сообщения, оставляем последнее (клавиатуру)
    await clear_user_messages(message, keep_last=True)

    # Запускаем предсказание
    msg = await message.answer("⏳ Анализирую данные...")
    add_user_message(message.from_user.id, msg.message_id)

    result = predictor.predict(coin_choice)

    # Удаляем "анализирую" и отправляем результат
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    except Exception:
        pass

    result_msg = await message.answer(result)
    add_user_message(message.from_user.id, result_msg.message_id)
