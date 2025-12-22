"""
Обработчик статистики питания.

ВАЖНО для FastAPI разработчика:
1. Эндпоинт /stats должен агрегировать данные из БД
2. Для бота важен текстовый вывод (поле ai_analysis в ответе)
3. Периоды: 'day', 'two_days', 'week' - должны корректно фильтровать данные
4. Не забудь про поле 'format': 'text' в запросе - боту нужен текстовый формат
"""

from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext

from src.keyboards import get_main_keyboard, get_stats_period_keyboard
from src.api_client import APIClient
import os
from .start import UserStates

router = Router()
API_URL = os.getenv("API_URL", "http://api:8000")

@router.message(F.text == "📊 Статистика питания")
async def stats_start(message: types.Message, state: FSMContext):
    """Начало просмотра статистики"""
    
    info_text = (
        "📈 <b>Статистика питания</b>\n\n"
        "Выберите период для просмотра статистики:\n"
        "• <b>За сегодня</b> - анализ текущего дня\n"
        "• <b>За 2 дня</b> - краткосрочные тренды\n"
        "• <b>За неделю</b> - долгосрочная динамика\n\n"
        "ИИ проанализирует ваши данные и даст рекомендации."
    )
    
    await message.answer(
        info_text,
        reply_markup=get_stats_period_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_stats_period)

@router.message(UserStates.waiting_for_stats_period)
async def process_stats_period(message: types.Message, state: FSMContext):
    """Обработка выбора периода статистики"""
    
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer(
            "Возвращаемся в главное меню...",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Маппинг текста кнопок на значения периода
    period_map = {
        "📅 За сегодня": "day",
        "📆 За 2 дня": "two_days",
        "🗓️ За неделю": "week"
    }
    
    period = period_map.get(message.text)
    
    if not period:
        await message.answer(
            "Пожалуйста, выберите период из предложенных вариантов.",
            reply_markup=get_stats_period_keyboard()
        )
        return
    
    
    processing_msg = await message.answer(
        f"📊 <i>Загружаем статистику за {message.text.lower()}...</i>",
        parse_mode="HTML"
    )
    
    # Здесь должен быть user_id из привязанного аккаунта
    user_id = f"telegram_{message.from_user.id}"
    
    async with APIClient(API_URL) as api:
        response = await api.get_statistics(
            user_id=user_id,
            period=period,
            telegram_id=message.from_user.id
        )
    
    # Удаляем сообщение о загрузке
    await processing_msg.delete()
    
    if response.get("status") == "success":
        data = response["data"]
        await send_stats_results(message, data, period)
    else:
        error_msg = response.get("detail", "Неизвестная ошибка")
        await message.answer(
            f"❌ <b>Ошибка загрузки статистики:</b>\n{error_msg}",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    
    await state.clear()

async def send_stats_results(message: types.Message, data: dict, period: str):
    """Форматирование и отправка результатов статистики"""
    
    period_names = {
        "day": "сегодня",
        "two_days": "2 дня",
        "week": "неделю"
    }
    
    period_name = period_names.get(period, period)
    
    # Заголовок
    header = f"📊 <b>Статистика за {period_name}</b>\n\n"
    
    # Основные метрики
    metrics = "📈 <b>Основные показатели:</b>\n"
    
    if "total_plates" in data:
        metrics += f"• Всего приемов пищи: {data['total_plates']}\n"
    
    if "avg_calories" in data:
        metrics += f"• Средние калории: {data['avg_calories']:.0f} ккал\n"
    
    if "balance_score" in data:
        score = data["balance_score"]
        score_emoji = "🟢" if score > 80 else "🟡" if score > 60 else "🔴"
        metrics += f"• Баланс питания: {score_emoji} {score}/100\n"
    
    if "trend" in data:
        trend = data["trend"]
        trend_emoji = {
            "improving": "📈 Улучшается",
            "stable": "➡️ Стабильно",
            "declining": "📉 Ухудшается"
        }.get(trend, trend)
        metrics += f"• Тренд: {trend_emoji}\n"
    
    metrics += "\n"
    
    # Анализ от ИИ
    analysis = ""
    if "ai_analysis" in data:
        analysis = f"🤖 <b>Анализ ИИ:</b>\n{data['ai_analysis']}\n\n"
    
    # Частые дефициты
    deficiencies = ""
    if "common_deficiencies" in data and data["common_deficiencies"]:
        deficiencies = "⚠️ <b>Частые дефициты:</b>\n"
        for i, deficiency in enumerate(data["common_deficiencies"][:3], 1):  # Ограничиваем 3
            name = deficiency.get("name", "Неизвестный")
            frequency = deficiency.get("frequency", 0)
            
            deficiencies += f"{i}. {name} ({frequency} раз)\n"
        
        deficiencies += "\n"
    
    # Рекомендации
    recommendations = ""
    if "recommendations" in data and data["recommendations"]:
        recommendations = "💡 <b>Рекомендации:</b>\n"
        for i, rec in enumerate(data["recommendations"][:3], 1):  # Ограничиваем 3
            recommendations += f"{i}. {rec}\n"
    
    # Собираем полное сообщение
    full_message = header + metrics + analysis + deficiencies + recommendations
    
    await message.answer(
        full_message,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )