"""
API клиент для Telegram бота.
ВСЕ запросы зависят от работающего FastAPI сервера

ВАЖНО для FastAPI разработчика:
1. Все эндпоинты должны быть доступны по http://api:8000 в Docker сети
2. Форматы запросов/ответов json обговорены 
3. Основные эндпоинты: 
   - POST /auth/generate_code
   - POST /auth/link  
   - POST /analyze
   - POST /stats
"""

import aiohttp
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
#TODO: В docker-compose.yml убедись, что сервис api доступен по имени "api" на порту 8000
class APIClient:
    """Асинхронный клиент для работы с FastAPI бэкендом"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
   

#TODO: Все эндпоинты должны возвращать JSON в формате {"status": "...", "data": {...} 
    async def _make_request(self, method: str, endpoint: str, 
                           data: Optional[Dict] = None,
                           token: Optional[str] = None) -> Dict[str, Any]:
        """Универсальный метод для выполнения HTTP запросов"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return {
                        "status": "error",
                        "detail": f"HTTP {response.status}: {error_text[:100]}"
                    }
                    
        except aiohttp.ClientConnectionError:
            return {"status": "error", "detail": "Не удалось подключиться к серверу"}
        except aiohttp.ClientTimeoutError:
            return {"status": "error", "detail": "Таймаут при соединении с сервером"}
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return {"status": "error", "detail": f"Неизвестная ошибка: {str(e)}"}
    
    
    #TODO: Реализуй POST /auth/generate_code. Ожидает {"telegram_id": int, "telegram_username": str}
    async def generate_link_code(self, telegram_id: int, username: str) -> Dict[str, Any]:
        """
        Генерация кода для привязки аккаунта
        
        JSON запрос к POST /auth/generate_code:
        {
            "telegram_id": 123456789,
            "telegram_username": "@username"
        }
        """
        data = {
            "telegram_id": telegram_id,
            "telegram_username": username
        }
        return await self._make_request("POST", "/auth/generate_code", data)
    
    
    #TODO: Реализуй POST /analyze с вызовом YandexGPT API. Формат запроса см. в API_CONTRACTS.md
    async def analyze_plate(self, user_id: str, text: str, 
                           telegram_id: int) -> Dict[str, Any]:
        """
        Анализ тарелки через ИИ
        
        JSON запрос к POST /analyze:
        {
            "user_id": "user_123",
            "text": "овсянка с бананом",
            "source": "telegram",
            "telegram_id": 123456789,
            "analyze_calories": true,
            "analyze_nutrients": true
        }
        """
        data = {
            "user_id": user_id,
            "text": text,
            "source": "telegram",
            "telegram_id": telegram_id,
            "analyze_calories": True,
            "analyze_nutrients": True
        }
        return await self._make_request("POST", "/analyze", data)
    
    
    #TODO: Реализуй POST /stats для агрегации данных из БД за период
    async def get_statistics(self, user_id: str, period: str, 
                            telegram_id: int) -> Dict[str, Any]:
        """
        Получение статистики за период
        
        JSON запрос к POST /stats:
        {
            "user_id": "user_123",
            "period": "day",
            "source": "telegram",
            "telegram_id": 123456789,
            "format": "text"  # Для бота нужен текстовый формат
        }
        """
        data = {
            "user_id": user_id,
            "period": period,
            "source": "telegram",
            "telegram_id": telegram_id,
            "format": "text"  # Указываем, что нужен текстовый ответ
        }
        return await self._make_request("POST", "/stats", data)
    
    
    #TODO: Реализуй POST /auth/link для проверки кода и привязки пользователя
    async def link_account(self, code: str, telegram_id: int) -> Dict[str, Any]:
        """
        Привязка аккаунта по коду
        
        JSON запрос к POST /auth/link:
        {
            "code": "123456",
            "telegram_id": 123456789
        }
        """
        data = {
            "code": code,
            "telegram_id": telegram_id
        }
        return await self._make_request("POST", "/auth/link", data)