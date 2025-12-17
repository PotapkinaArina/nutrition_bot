import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties

# TODO для FastAPI разработчика:
# 1. Бот ожидает, что API будет доступно по адресу из переменной API_URL
# 2. При запуске docker-compose, сервис api должен стартовать ДО сервиса bot (depends_on)
# 3. Реализуй GET /health для проверки доступности API

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__) #создаем именованный логгер под модуль main


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://api:8000") #TODO: В docker-compose.yml добавь переменную API_URL для сервиса bot

if not BOT_TOKEN:
    logger.error("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")
    exit(1)


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher() 
async def register_handlers():
    from handlers import start, analysis, stats, auth
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(analysis.router)
    dp.include_router(stats.router)
    logger.info("Все обработчики зарегистрированы")


#TODO: Перед запуском бота убедись, что сервис api здоров (реализуй GET /health)
async def main():
    logger.info("Запуск бота")
    await register_handlers()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info(f"Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())