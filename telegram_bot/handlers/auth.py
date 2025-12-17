"""
Обработчик привязки аккаунта к веб-интерфейсу.

ВАЖНО для FastAPI разработчика:
1. /auth/generate_code - генерация 6-значного кода, привязанного к telegram_id
2. /auth/link - проверка кода, создание/связывание user_id
3. Код должен храниться в БД с timestamp для истечения срока действия
"""
from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext

from src.keyboards import get_main_keyboard, get_cancel_keyboard
from src.api_client import APIClient
import os
from .start import UserStates

router = Router()
API_URL = os.getenv("API_URL", "http://api:8000")

@router.message(F.text == "🔗 Привязать аккаунт")
async def link_account_start(message: types.Message, state: FSMContext):
    """Начало процесса привязки аккаунта"""
    
    help_text = (
        "🔗 <b>Привязка аккаунта к веб-версии</b>\n\n"
        "Для привязки:\n"
        "1. <b>Введите 6-значный код</b>, который вы получили на сайте\n"
        "2. Или нажмите <b>'Сгенерировать новый код'</b>, если у вас его нет\n\n"
        "Введите код или выберите действие:"
    )
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🆕 Сгенерировать новый код")],
            [types.KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    await message.answer(help_text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(UserStates.waiting_for_link_code)

#TODO: /auth/generate_code должен вернуть {"status": "success", "data": {"code": "123456", "expires_at": "..."}}
@router.message(F.text == "🆕 Сгенерировать новый код")
async def generate_new_code(message: types.Message):
    """Генерация нового кода для привязки"""
   
    async with APIClient(API_URL) as api:
        response = await api.generate_link_code(
            telegram_id=message.from_user.id,
            username=message.from_user.username or message.from_user.full_name
        )
    if response.get("status") == "success":
        code = response["data"]["code"]
        expires_at = response["data"]["expires_at"]
        
        code_message = (
            "✅ <b>Код успешно сгенерирован!</b>\n\n"
            f"🔢 <b>Ваш код:</b> <code>{code}</code>\n"
            f"⏰ <b>Действителен до:</b> {expires_at}\n\n"
            "<b>Как использовать:</b>\n"
            "1. Перейдите на сайт анализатора питания\n"
            "2. Найдите раздел 'Привязка аккаунта'\n"
            "3. Введите этот код\n"
            "4. Готово! Ваши данные синхронизированы\n\n"
            "<i>Код можно использовать только один раз</i>"
        )
    else:
        code_message = (
            "❌ <b>Ошибка генерации кода</b>\n\n"
            f"Причина: {response.get('detail', 'Неизвестная ошибка')}\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
    
    await message.answer(code_message, reply_markup=get_main_keyboard(), parse_mode="HTML")


#TODO: /auth/link должен проверять код и возвращать user_id
@router.message(UserStates.waiting_for_link_code)
async def process_link_code(message: types.Message, state: FSMContext):
    """Обработка введенного кода привязки"""
    
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    code = message.text.strip()
    
    if len(code) != 6 or not code.isdigit():
        await message.answer(
            "❌ Код должен состоять из 6 цифр.\nПопробуйте еще раз или нажмите 'Отмена'.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    async with APIClient(API_URL) as api:
        response = await api.link_account(
            code=code,
            telegram_id=message.from_user.id
        )
    
    if response.get("status") == "success":
        user_id = response["data"]["user_id"]
        
        success_message = (
            "✅ <b>Аккаунт успешно привязан!</b>\n\n"
            f"🆔 <b>Ваш ID:</b> <code>{user_id}</code>\n"
            "🌐 <b>Теперь вы можете:</b>\n"
            "• Использовать веб-версию анализатора\n"
            "• Видеть общую историю анализов\n"
            "• Синхронизировать данные между платформами\n\n"
            "<i>Приятного использования!</i>"
        )
        
        await state.clear()
        await message.answer(
            success_message,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        error_detail = response.get("detail", "Неизвестная ошибка")
        await message.answer(
            f"❌ <b>Ошибка привязки:</b>\n{error_detail}\n\n"
            "Проверьте код и попробуйте еще раз.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )