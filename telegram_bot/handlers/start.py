from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext #контекст машины состояний
from aiogram.fsm.state import State, StatesGroup #класс для определения отдельного состояния и группировки связанных

from src.keyboards import get_main_keyboard 

router = Router()

class UserStates(StatesGroup):
    """Состояния пользователя для FSM"""
    waiting_for_plate_text = State()
    waiting_for_stats_period = State()
    waiting_for_link_code = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    welcome_text = (
        "👋 <b>Добро пожаловать в Анализатор питания!</b>\n\n"
        "Я помогу вам:\n"
        "• 📊 <b>Анализировать</b> состав и калорийность ваших приемов пищи\n"
        "• 📈 <b>Отслеживать</b> статистику питания за разные периоды\n"
        "• 🔄 <b>Синхронизировать</b> данные с веб-версией\n\n"
        "Используйте кнопки ниже для навигации:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), 
        parse_mode="HTML")