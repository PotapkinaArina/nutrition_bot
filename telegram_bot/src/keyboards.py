from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с главными функциями"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽️ Анализ тарелки")],
            [KeyboardButton(text="📊 Статистика питания")],
            [KeyboardButton(text="🔗 Привязать аккаунт")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_stats_period_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора периода статистики"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 За сегодня")],
            [KeyboardButton(text="📆 За 2 дня")],
            [KeyboardButton(text="🗓️ За неделю")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )