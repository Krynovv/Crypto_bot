from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from lexicon.lexicon import LEXICON_RU

#==================================================================================
#---------------------------|__Клавиатура-start__|---------------------------------

# Создаем кнопки
button_direction = KeyboardButton(text=LEXICON_RU["button_direction"])
button_no = KeyboardButton(text=LEXICON_RU["button_no"])

# Инициализируем билдер для клавиатуры с кнопками
kb_builder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер с аргументом width=2
kb_builder.row(button_direction, button_no, width=2)

# Создаем клавиатуру с кнопками
kb: ReplyKeyboardMarkup = kb_builder.as_markup(
   one_time_keyboard=True, resize_keyboard=True
)

#===================================================================================
#---------------------------|__Клавиатура-direction__|------------------------------

# Кнопки-coins
button_BTC = KeyboardButton(text=LEXICON_RU["button_BTC"])
button_ETH = KeyboardButton(text=LEXICON_RU["button_ETH"])

direct_kb = ReplyKeyboardMarkup(
   keyboard=[[button_BTC], [button_ETH]], resize_keyboard=True
)