import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Optional, Dict, Any

# TODO для FastAPI разработчика:
# 1. Docker Compose должен создавать сервис с именем 'api' на порту 8000
# 2. Все эндпоинты должны возвращать JSON в формате: {"status": "success"/"error", "data": {...}, "detail": "..."}
# 3. Основные эндпоинты: POST /auth/link, POST /analyze, POST /stats, GET /health


API_BASE_URL = os.getenv("API_URL", "http://api:8000")  # 'api' - имя сервиса в docker-compose.yml


st.set_page_config(
    page_title="🍽️ Анализатор питания",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


if 'auth' not in st.session_state:
    st.session_state.auth = {
        'is_authenticated': False,
        'user_id': None,
        'telegram_username': None,
        'access_token': None  
    }

if 'recent_plates' not in st.session_state:
    st.session_state.recent_plates = []  


def make_api_request(endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, 
                     token: Optional[str] = None) -> Dict[str, Any]:
    """
    Универсальная функция для вызова API бэкенда.
    
    Args:
        endpoint: API endpoint (например, '/auth/link')
        method: HTTP метод ('GET', 'POST', 'PUT', 'DELETE')
        data: Данные для отправки (будут преобразованы в JSON)
        token: JWT токен авторизации (если требуется)
    
    Returns:
        Словарь с ответом API или ошибкой
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return {"status": "error", "detail": f"Метод {method} не поддерживается"}
        
        # Пытаемся распарсить JSON ответ
        return response.json()
        
    except requests.exceptions.ConnectionError:
        return {"status": "error", "detail": "Не удалось подключиться к серверу API"}
    except requests.exceptions.Timeout:
        return {"status": "error", "detail": "Таймаут при соединении с API"}
    except json.JSONDecodeError:
        return {"status": "error", "detail": "Некорректный ответ от сервера"}
    except Exception as e:
        return {"status": "error", "detail": f"Неизвестная ошибка: {str(e)}"}

def fetch_user_stats(period: str) -> Optional[Dict]:
    """Запрашивает статистику пользователя за указанный период"""
    if not st.session_state.auth['is_authenticated']:
        return None
    
    # Формируем JSON запрос для API статистики
    request_data = {
        "user_id": st.session_state.auth['user_id'],
        "period": period,  # 'day', 'two_days', 'week'
        "include_charts": True
    }
    
    # Отправляем POST запрос к эндпоинту /stats
    response = make_api_request(
        endpoint="/stats",
        method="POST",
        data=request_data,
        token=st.session_state.auth.get('access_token')
    )
    
    if response.get("status") == "success":
        return response.get("data", {})
    else:
        st.error(f"Ошибка загрузки статистики: {response.get('detail', 'Неизвестная ошибка')}")
        return None


def render_auth_interface():
    """Отображает интерфейс привязки Telegram аккаунта"""
    st.sidebar.header("🔐 Привязка аккаунта")
    
    with st.sidebar.expander("Инструкция", expanded=True):
        st.markdown("""
        1. **В Telegram боте** отправьте команду `/get_code`
        2. **Скопируйте** полученный 6-значный код
        3. **Введите код ниже** и нажмите "Привязать"
        
        После привязки ваша история анализов будет синхронизироваться
        между ботом и сайтом.
        """)
    
    # Поле для ввода кода
    link_code = st.sidebar.text_input(
        "Код из Telegram",
        max_chars=6,
        placeholder="123456",
        help="6-значный код из Telegram бота"
    )
    
    col1, col2 = st.sidebar.columns([1, 2])
    with col1:
        if st.button("🔗 Привязать", use_container_width=True):
            if link_code and len(link_code) == 6:
                with st.spinner("Проверяем код..."):
                    # Формируем JSON запрос для проверки кода
                    auth_request = {"code": link_code}
                    
                    # Отправляем POST запрос к эндпоинту /auth/link
                    response = make_api_request(
                        endpoint="/auth/link", 
                        method="POST", 
                        data=auth_request
                    )
                    
                    # Обрабатываем JSON ответ от бэкенда
                    if response.get("status") == "success":
                        auth_data = response.get("data", {})
                        st.session_state.auth.update({
                            'is_authenticated': True,
                            'user_id': auth_data.get("user_id"),
                            'telegram_username': auth_data.get("telegram_username"),
                            'access_token': auth_data.get("access_token")
                        })
                        st.success("✅ Аккаунт успешно привязан!")
                        st.rerun()  # Перезагружаем страницу для обновления интерфейса
                    else:
                        st.error(f"❌ {response.get('detail', 'Неверный код')}")
            else:
                st.warning("Введите 6-значный код")


def render_plate_analysis():
    """Интерфейс для анализа одного приема пищи"""
    st.header("🔍 Анализ тарелки")
    
    with st.form("plate_analysis_form"):
        # Текстовое поле для описания еды
        plate_description = st.text_area(
            "Опишите, что вы съели:",
            height=150,
            placeholder="Пример: На завтрак: овсянка на молоке с бананом и ложкой меда, "
                       "кофе с сахаром. На обед: куриная грудка с гречкой и салатом из "
                       "помидоров и огурцов с оливковым маслом.",
            help="Опишите максимально подробно все приемы пищи за один раз"
        )
        
        # Дополнительные параметры анализа
        col1, col2 = st.columns(2)
        with col1:
            analyze_calories = st.checkbox("Рассчитать калории", value=True)
        with col2:
            analyze_nutrients = st.checkbox("Анализировать нутриенты", value=True)
        
        submitted = st.form_submit_button("🧪 Проанализировать", type="primary")
        
        if submitted and plate_description:
            with st.spinner("Анализируем состав и калории..."):
                # Формируем JSON запрос для анализа
                analysis_request = {
                    "user_id": st.session_state.auth['user_id'],
                    "text": plate_description,
                    "analyze_calories": analyze_calories,
                    "analyze_nutrients": analyze_nutrients,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Отправляем POST запрос к эндпоинту /analyze
                response = make_api_request(
                    endpoint="/analyze",
                    method="POST",
                    data=analysis_request,
                    token=st.session_state.auth.get('access_token')
                )
                
                # Обрабатываем JSON ответ от бэкенда
                if response.get("status") == "success":
                    analysis_data = response.get("data", {})
                    
                    # Сохраняем в кэш
                    st.session_state.recent_plates.append({
                        "description": plate_description[:100] + "..." if len(plate_description) > 100 else plate_description,
                        "data": analysis_data,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    
                    # Отображаем результаты
                    display_analysis_results(analysis_data)
                else:
                    st.error(f"Ошибка анализа: {response.get('detail', 'Неизвестная ошибка')}")

def display_analysis_results(data: Dict):
    """Отображает результаты анализа в красивом формате"""
    # 1. Сводка анализа
    if "summary" in data:
        with st.expander("📝 Сводка анализа", expanded=True):
            st.info(data["summary"])
    
    # 2. Метрики калорий и БЖУ
    if "calories" in data or "macros" in data:
        st.subheader("📊 Пищевая ценность")
        cols = st.columns(4)
        
        metrics = [
            ("Калории", data.get("calories"), "ккал"),
            ("Белки", data.get("macros", {}).get("protein"), "г"),
            ("Жиры", data.get("macros", {}).get("fat"), "г"),
            ("Углеводы", data.get("macros", {}).get("carbs"), "г")
        ]
        
        for idx, (label, value, unit) in enumerate(metrics):
            with cols[idx]:
                if value is not None:
                    st.metric(label, f"{value} {unit}")
                else:
                    st.metric(label, "—")
    
    # 3. Детализированный состав
    if "detailed_nutrients" in data:
        st.subheader("🧪 Детальный состав")
        nutrients_df = pd.DataFrame(data["detailed_nutrients"])
        st.dataframe(
            nutrients_df.style.format({
                'amount': '{:.1f}',
                'daily_percent': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    # 4. Дефициты и рекомендации
    if "deficiencies" in data and data["deficiencies"]:
        st.subheader("⚠️ Выявленные дефициты")
        
        for deficiency in data["deficiencies"]:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    severity = deficiency.get("severity", "medium")
                    colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    st.markdown(f"### {colors.get(severity, '⚪')}")
                
                with col2:
                    st.markdown(f"**{deficiency.get('name')}**")
                    st.progress(deficiency.get("confidence", 0.5))
                    st.caption(f"Причина: {deficiency.get('reason', 'Не указана')}")
        
        # Рекомендации
        if "recommendations" in data:
            st.subheader("💡 Рекомендации")
            for rec in data["recommendations"]:
                st.markdown(f"• {rec}")


def render_statistics():
    """Отображает статистику за разные периоды"""
    st.header("📈 Статистика питания")
    
    # Выбор периода
    period = st.radio(
        "Период анализа:",
        ["day", "two_days", "week"],
        format_func=lambda x: {
            "day": "За сегодня",
            "two_days": "За 2 дня", 
            "week": "За неделю"
        }[x],
        horizontal=True
    )
    
    if st.button("🔄 Обновить статистику", type="secondary"):
        stats_data = fetch_user_stats(period)
        
        if stats_data:
            display_statistics(stats_data, period)

def display_statistics(data: Dict, period: str):
    """Отображает статистику в графиках и метриках"""
    # Основные метрики
    st.subheader("Основные показатели")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего тарелок", data.get("total_plates", 0))
    with col2:
        st.metric("Средние калории", f"{data.get('avg_calories', 0):.0f} ккал")
    with col3:
        st.metric("Баланс БЖУ", data.get("balance_score", 0))
    with col4:
        trend = data.get("trend", "stable")
        trend_icons = {"improving": "📈", "declining": "📉", "stable": "➡️"}
        st.metric("Тренд", trend_icons.get(trend, "➡️"))
    
    # График калорий по времени
    if "calories_over_time" in data:
        st.subheader("Калорийность по дням")
        df_calories = pd.DataFrame(data["calories_over_time"])
        
        fig = px.line(
            df_calories, 
            x="date", 
            y="calories",
            title=f"Динамика калорий ({period})",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Дата",
            yaxis_title="Калории (ккал)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Круговая диаграмма БЖУ
    if "macros_distribution" in data:
        st.subheader("Распределение БЖУ")
        df_macros = pd.DataFrame([data["macros_distribution"]])
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(df_macros.columns),
                values=df_macros.iloc[0].tolist(),
                hole=.3
            )
        ])
        fig.update_layout(title="Соотношение белков, жиров и углеводов")
        st.plotly_chart(fig, use_container_width=True)
    
    # Таблица дефицитов
    if "common_deficiencies" in data:
        st.subheader("Частые дефициты")
        deficiencies_df = pd.DataFrame(data["common_deficiencies"])
        
        if not deficiencies_df.empty:
            # Создаем индикаторы серьезности
            deficiency_colors = {
                "high": "🔴 Высокий",
                "medium": "🟡 Средний", 
                "low": "🟢 Низкий"
            }
            deficiencies_df["Уровень"] = deficiencies_df["severity"].map(deficiency_colors)
            
            st.dataframe(
                deficiencies_df[["name", "Уровень", "frequency"]].rename(
                    columns={"name": "Дефицит", "frequency": "Частота"}
                ),
                use_container_width=True,
                hide_index=True
            )


def main():
    
    st.title("🍽️ Умный анализатор питания")
    st.markdown("Анализируйте состав пищи, отслеживайте калории и получайте персональные рекомендации")
    
    # Если пользователь не аутентифицирован - показываем интерфейс привязки
    if not st.session_state.auth['is_authenticated']:
        render_auth_interface()
        
        # Показываем демо-информацию для непривязанных пользователей
        st.info("""
        ### 🚀 Для начала работы:
        1. Привяжите ваш Telegram аккаунт (см. боковую панель слева)
        2. После привязки откроется полный функционал:
           - 📊 Анализ состава и калорийности пищи
           - 📈 Статистика за день/неделю
           - 🔄 Синхронизация с Telegram ботом
        """)
        
        # Демо-скриншоты или информация о функционале
        with st.expander("📱 Как получить код в Telegram боте"):
            st.image("https://via.placeholder.com/600x300?text=Telegram+Bot+Screenshot", 
                    caption="Отправьте боту команду /get_code")
        
        return
    
    # Если пользователь аутентифицирован - показываем основной интерфейс
    st.sidebar.success(f"✅ Привязано к: {st.session_state.auth['telegram_username']}")
    
    if st.sidebar.button("🚪 Выйти"):
        st.session_state.auth = {'is_authenticated': False, 'user_id': None}
        st.session_state.recent_plates = []
        st.rerun()
    
    # Навигация по вкладкам
    tab1, tab2, tab3 = st.tabs([
        "🔍 Анализ тарелки", 
        "📈 Статистика", 
        "🕐 Недавние анализы"
    ])
    
    with tab1:
        render_plate_analysis()
    
    with tab2:
        render_statistics()
    
    with tab3:
        st.header("Недавние анализы")
        if st.session_state.recent_plates:
            for i, plate in enumerate(reversed(st.session_state.recent_plates[-5:])):
                with st.expander(f"{plate['time']}: {plate['description']}", expanded=i==0):
                    if "calories" in plate['data']:
                        st.metric("Калории", f"{plate['data']['calories']} ккал")
                    if "deficiencies" in plate['data']:
                        st.write(f"Выявлено дефицитов: {len(plate['data']['deficiencies'])}")
        else:
            st.info("Здесь появятся ваши последние анализы")


if __name__ == "__main__":
    # Проверяем доступность API при запуске
    try:
        health_check = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_check.status_code != 200:
            st.warning("⚠️ API бэкенд недоступен. Некоторые функции могут не работать.")
    except:
        st.error("🚨 Не удалось подключиться к API бэкенду. Убедитесь, что сервис 'api' запущен.")
    
    main()