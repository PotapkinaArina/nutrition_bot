import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверяем, что токен загружен
if not BOT_TOKEN:
    logger.error("Токен бота не найден! Проверьте файл .env")
    exit(1)  # Останавливаем программу, если токена нет

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ==================== КЛАВИАТУРА С КНОПКОЙ ====================
# Создаем клавиатуру с одной кнопкой "Старт"
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Старт")]
    ],
    resize_keyboard=True,  # Автоматический размер кнопки
    one_time_keyboard=False  # Клавиатура не исчезнет после нажатия
)

# ==================== ФУНКЦИЯ ПРИВЕТСТВИЯ ====================
def get_welcome_message() -> str:
    """Возвращает приветственное сообщение для пользователя"""
    return (
        "👋 <b>Привет! Я бот для анализа питания.</b>\n\n"
        "Я помогу понять, каких витаминов и микроэлементов "
        "вам может не хватать на основе вашего рациона.\n\n"
        "Просто <b>отправьте мне список продуктов</b>, которые вы съели за день, "
        "или нажмите кнопку <b>🚀 Старт</b>, чтобы начать!\n\n"
        "Например: <i>'яблоко, курица, гречка, салат из помидоров'</i>\n\n"
        "📌 <i>В этом тестовом режиме я покажу только это сообщение. "
        "Функция анализа скоро появится!</i>"
    )

# ==================== ОБРАБОТЧИК КОМАНДЫ /START ====================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обрабатывает команду /start"""
    await message.answer(
        text=get_welcome_message(),
        reply_markup=start_keyboard
    )
    logger.info(f"Пользователь {message.from_user.id} использовал /start")

# ==================== ОБРАБОТЧИК КНОПКИ "СТАРТ" ====================
@dp.message(lambda message: message.text and "старт" in message.text.lower())
async def handle_start_button(message: types.Message):
    """Обрабатывает нажатие кнопки 'Старт' или текст 'старт'"""
    await message.answer(
        text=get_welcome_message(),
        reply_markup=start_keyboard
    )
    logger.info(f"Пользователь {message.from_user.id} нажал кнопку Старт")

# ==================== ЗАГЛУШКА ДЛЯ ЛЮБЫХ ДРУГИХ СООБЩЕНИЙ ====================
@dp.message()
async def handle_other_messages(message: types.Message):
    """Заглушка для всех остальных сообщений"""
    await message.answer(
        "⏳ <b>Функция анализа питания в разработке!</b>\n\n"
        "Сейчас я могу только показать приветствие. "
        "Нажмите кнопку <b>🚀 Старт</b> или отправьте команду <code>/start</code>."
    )
    logger.info(f"Пользователь {message.from_user.id} отправил: {message.text[:50]}...")

# ==================== ЗАПУСК БОТА ====================
async def main():
    """Основная функция запуска бота"""
    logger.info("Запускаю бота...")
    
    # Удаляем старые обновления, чтобы избежать ошибок
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Начинаем опрашивать Telegram на новые сообщения
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем асинхронную функцию main()
    asyncio.run(main())