import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import uuid
from typing import Optional, Dict, Any

API_BASE_URL = os.getenv("API_URL", "http://api:8000")  # 'api' - имя сервиса в docker-compose.yml

# параметры страницы
st.set_page_config(
    page_title="🍽️ Анализатор питания",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'user_id' not in st.session_state:
    st.session_state.user_id = f"web_guest_{uuid.uuid4().hex[:8]}"

if 'recent_plates' not in st.session_state:
    st.session_state.recent_plates = []


def make_api_request(endpoint: str, method: str = "GET",
                     data: Dict = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return {"status": "error", "detail": f"Метод {method} не поддерживается"}

        # пытаемся распарсить JSON ответ
        return response.json()

    except requests.exceptions.ConnectionError:
        return {"status": "error", "detail": "Не удалось подключиться к серверу API"}
    except requests.exceptions.Timeout:
        return {"status": "error", "detail": "Таймаут при соединении с API"}
    except json.JSONDecodeError:
        return {"status": "error", "detail": "Некорректный ответ от сервера"}
    except Exception as e:
        return {"status": "error", "detail": f"Неизвестная ошибка: {str(e)}"}


def render_plate_analysis():
    """Интерфейс для анализа одного приема пищи"""
    st.header("🔍 Анализ тарелки")

    with st.form("plate_analysis_form"):
        # текстовое поле для описания еды
        plate_description = st.text_area(
            "Опишите, что вы съели:",
            height=150,
            placeholder="Пример: На завтрак: овсянка на молоке с бананом и ложкой меда, "
                        "кофе с сахаром. На обед: куриная грудка с гречкой и салатом из "
                        "помидоров и огурцов с оливковым маслом.",
            help="Опишите максимально подробно все приемы пищи за один раз"
        )

        # дополнительные параметры анализа
        col1, col2 = st.columns(2)
        with col1:
            analyze_calories = st.checkbox("Рассчитать калории", value=True)
        with col2:
            analyze_nutrients = st.checkbox("Анализировать нутриенты", value=True)

        submitted = st.form_submit_button("🧪 Проанализировать", type="primary")

        if submitted and plate_description:
            with st.spinner("Анализируем состав и калории..."):
                # формируем JSON запрос для анализа
                analysis_request = {
                    "user_id": st.session_state.user_id,
                    "text": plate_description,
                    "analyze_calories": analyze_calories,
                    "analyze_nutrients": analyze_nutrients,
                    "source": "web"
                }

                # отправляем POST запрос к эндпоинту /analyze
                response = make_api_request(
                    endpoint="/analyze",
                    method="POST",
                    data=analysis_request,
                )

                # обрабатываем JSON ответ от бэкенда
                if response.get("status") == "success":
                    analysis_data = response.get("data", {})

                    # Сохраняем в кэш
                    st.session_state.recent_plates.append({
                        "description": plate_description[:100] + "..." if len(
                            plate_description) > 100 else plate_description,
                        "data": analysis_data,
                        "time": datetime.now().strftime("%H:%M")
                    })

                    # отображаем результаты
                    display_analysis_results(analysis_data)
                else:
                    st.error(f"Ошибка анализа: {response.get('detail', 'Неизвестная ошибка')}")


def display_analysis_results(data: Dict):
    """Отображает результаты анализа в красивом формате"""
    # сводка анализа
    if "summary" in data:
        with st.expander("📝 Сводка анализа", expanded=True):
            st.info(data["summary"])

    # метрики калорий и БЖУ
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

    # дефициты и рекомендации
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
                    if "confidence" in deficiency:
                        st.progress(float(deficiency["confidence"]))
                        st.caption(f"Уверенность: {deficiency['confidence'] * 100:.0f}%")

                        # рекомендации
        if "recommendations" in data:
            st.subheader("💡 Рекомендации")
            for rec in data["recommendations"]:
                st.markdown(f"• {rec}")


def main():
    """Главная функция - без проверки авторизации"""

    st.title("🍽️ Умный анализатор питания")
    st.markdown("Анализируйте состав пищи, отслеживайте калории и получайте персональные рекомендации")

    # сайдбар с информацией и управлением сессией
    with st.sidebar:
        st.header("ℹ️ О сервисе")
        st.markdown("""
        Этот сервис помогает:

        - 📊 **Анализировать** калорийность пищи
        - 🥗 **Оценивать** баланс белков, жиров, углеводов
        - 🔍 **Выявлять** дефициты питательных веществ
        - 💡 **Получать** персональные рекомендации

        *Работает на основе искусственного интеллекта*
        """)

        # информация о текущей сессии
        st.divider()
        st.caption(f"Текущая сессия: `{st.session_state.user_id[:15]}...`")

        # кнопки управления сессией
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Новая сессия", use_container_width=True):
                st.session_state.user_id = f"web_guest_{uuid.uuid4().hex[:8]}"
                st.session_state.recent_plates = []
                st.rerun()

        with col2:
            if st.button("🗑️ Очистить историю", use_container_width=True):
                st.session_state.recent_plates = []
                st.rerun()

    tab1, tab2 = st.tabs([
        "🔍 Анализ тарелки",
        "🕐 Недавние анализы"
    ])

    with tab1:
        render_plate_analysis()

    with tab2:
        st.header("Недавние анализы")
        if st.session_state.recent_plates:
            for i, plate in enumerate(reversed(st.session_state.recent_plates[-5:])):
                with st.expander(f"{plate['time']}: {plate['description']}", expanded=i == 0):
                    if "calories" in plate['data']:
                        st.metric("Калории", f"{plate['data']['calories']} ккал")
                    if "deficiencies" in plate['data']:
                        st.write(f"Выявлено дефицитов: {len(plate['data']['deficiencies'])}")

                    if "summary" in plate['data']:
                        st.caption(plate['data']['summary'][:150] + "...")
        else:
            st.info("Здесь появятся ваши последние анализы")


if __name__ == "__main__":
    main()