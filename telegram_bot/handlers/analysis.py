from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext

from src.keyboards import get_main_keyboard, get_cancel_keyboard
from src.api_client import APIClient
import os
from .start import UserStates

"""
Обработчик анализа тарелки через ИИ.

ВАЖНО для FastAPI разработчика:
1. Эндпоинт /analyze - самый важный, должен работать с YandexGPT API
2. Формат ответа ДОЛЖЕН быть именно таким, как в API_CONTRACTS.md
3. Обязательные поля в ответе: summary, calories, macros, deficiencies[], recommendations[]
4. Не забудь сохранять анализ в БД для истории и статистики
"""

router = Router()
API_URL = os.getenv("API_URL", "http://api:8000")

@router.message(F.text == "🍽️ Анализ тарелки")
async def analyze_plate_start(message: types.Message, state: FSMContext):
    """Начало анализа тарелки"""
    
    instructions = (
        "🍽️ <b>Анализ приема пищи</b>\n\n"
        "Опишите, что вы съели:\n"
        "• 📝 <b>Подробно</b> перечислите все продукты\n"
        "• ⚖️ Укажите <b>примерные объемы</b>\n"
        "• 🧂 Упомяните <b>соусы и добавки</b>\n\n"
        "<i>Пример: 'На завтрак: овсянка на молоке (150г), "
        "банан (1 шт), кофе с сахаром (1 ч.л.)'</i>\n\n"
        "Введите описание или нажмите 'Отмена':"
    )
    
    await message.answer(
        instructions,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_plate_text)

@router.message(UserStates.waiting_for_plate_text)
async def process_plate_text(message: types.Message, state: FSMContext):
    """Обработка текста тарелки и отправка на анализ"""
    
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Анализ отменен.",
            reply_markup=get_main_keyboard()
        )
        return
    
    plate_text = message.text.strip()
    
    if len(plate_text) < 10:
        await message.answer(
            "❌ Описание слишком короткое. Пожалуйста, опишите подробнее.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    
    processing_msg = await message.answer(
        "🔍 <i>Анализируем ваш рацион...</i>",
        parse_mode="HTML"
    )
    
    # Здесь должен быть user_id из привязанного аккаунта
    # Временная заглушка - в реальности нужно получать из БД
    user_id = f"telegram_{message.from_user.id}"
    
    async with APIClient(API_URL) as api:
        response = await api.analyze_plate(
            user_id=user_id,
            text=plate_text,
            telegram_id=message.from_user.id
        )
    
    
    await processing_msg.delete()
    
    if response.get("status") == "success":
        data = response["data"]
        await send_analysis_results(message, data)
    else:
        error_msg = response.get("detail", "Неизвестная ошибка")
        await message.answer(
            f"❌ <b>Ошибка анализа:</b>\n{error_msg}",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    
    await state.clear()

async def send_analysis_results(message: types.Message, data: dict):
    """Форматирование и отправка результатов анализа"""
    
    # Сводка
    summary = f"📝 <b>Сводка анализа:</b>\n{data.get('summary', 'Нет данных')}\n\n"
    
    # Калории и БЖУ
    nutrition_info = "📊 <b>Пищевая ценность:</b>\n"
    if "calories" in data:
        nutrition_info += f"• Калории: {data['calories']} ккал\n"
    
    if "macros" in data:
        macros = data["macros"]
        nutrition_info += f"• Белки: {macros.get('protein', 0)}г\n"
        nutrition_info += f"• Жиры: {macros.get('fat', 0)}г\n"
        nutrition_info += f"• Углеводы: {macros.get('carbs', 0)}г\n"
    
    nutrition_info += "\n"
    
    # Дефициты
    deficiencies_info = ""
    if "deficiencies" in data and data["deficiencies"]:
        deficiencies_info = "⚠️ <b>Выявленные дефициты:</b>\n"
        for deficiency in data["deficiencies"]:
            name = deficiency.get("name", "Неизвестный")
            severity = deficiency.get("severity", "medium")
            confidence = deficiency.get("confidence", 0) * 100
            
            severity_icon = {
                "high": "🔴",
                "medium": "🟡", 
                "low": "🟢"
            }.get(severity, "⚪")
            
            deficiencies_info += (
                f"{severity_icon} <b>{name}</b> "
                f"({severity}, уверенность: {confidence:.0f}%)\n"
            )
        deficiencies_info += "\n"
    
    #  Рекомендации
    recommendations_info = ""
    if "recommendations" in data and data["recommendations"]:
        recommendations_info = "💡 <b>Рекомендации:</b>\n"
        for i, rec in enumerate(data["recommendations"][:5], 1):  # Ограничиваем 5 рекомендациями
            recommendations_info += f"{i}. {rec}\n"
    
    # Собираем всё сообщение
    full_message = summary + nutrition_info + deficiencies_info + recommendations_info
    
    # Разбиваем на части если сообщение слишком длинное
    max_length = 4000  
    
    if len(full_message) > max_length:
        # Отправляем частями
        parts = []
        current_part = ""
        
        for line in full_message.split('\n'):
            if len(current_part) + len(line) + 1 > max_length:
                parts.append(current_part)
                current_part = line
            else:
                current_part += '\n' + line if current_part else line
        
        if current_part:
            parts.append(current_part)
        
        for i, part in enumerate(parts):
            if i == 0:
                await message.answer(part, parse_mode="HTML")
            else:
                await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(full_message, parse_mode="HTML")
    
    await message.answer(
        "Что дальше? Выберите действие:",
        reply_markup=get_main_keyboard()
    )