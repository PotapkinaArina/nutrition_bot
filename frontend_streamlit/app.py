import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Nutrition Bot",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 nutriotion bot!")
st.markdown("Проанализируйте своё питание и получите рекомендации по нутриентам")

BACKEND_URL = "http://backend:8000"

with st.sidebar:
    st.header("Информация")
    st.info( """
    **Как это работает:**
    1. ВВедите продукты, которые Вы употребили;
    2. ИИ анализирует нутриенты;
    3. Получайте рекомендации по дефицитам.
    """)

    try:
        response = requests.get(f"{BACKEND_URL}/health",timeout=5)
        if response.status_code==200:
            st.success("BACKEND подключён ^^")
        else:
            st.error("Не доступен BACKEND :(")
    except:
        st.error("Не удалось подключиться к backend!")
    
tab1, tab2 = st.tabs([ "📊 Анализ питания", "📈 История"])

with tab1:
    st.header("Анализ питания")
    food_text = st.text_area(
        "Что вы сегодня ели?",
        placeholder="Что-то типа овсянка, каша с ягодами, грудка курицы, мандарины и тд.",
        height=150
    )

    if st.button("🔍 Проанализировать", type="primary"):
        if food_text.strip():
            with st.spinner("Анализируем Ваше питание..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/analyze",
                        json={"text": food_text, "source": "web"}
                    )

                    if response.status_code == 200:
                        data=response.json()
                        st.success("Анализ завершён!")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Калории", f"{data['calories']} ккал")
                        with col2:
                            st.metric("Белки", f"{data['protein']} г")
                        with col3:
                            st.metric("Жиры", f"{data['fat']} г")
                        with col4:
                            st.metric("Углеводы", f"{data['carbs']} г")

                        if data['deficiencies']:
                            st.subheader("📉 Выявленные дефициты")
                            for deficiency in data['deficiencies']:
                                with st.expander(f"{deficiency['name']} ({deficiency['severity']})"):
                                    st.write(f"**Рекомендованные продукты ** {deficiency['recommended_food']}")
                        else:
                            st.info("Класс! Серьёзных дефицитов не обнаружено!🎉🎉🎉")

                        st.subheader("Рекомендаци💡")
                        st.write(data['recommendations'])

                    else:
                        st.error(f"Ошибка при анализе : {response.text}")
                except Exception as e:
                    st.error(f"Ошибка подключения : {str(e)}")
                    st.info("Проверьте, запущен ли backend сервер.")

        else: 
            st.warning("Введите текст для анализа")
with tab2:
    st.header("История анализов")
    user_id=st.number_input("ID пользователя", min_value=1, value=1)

    if st.button("Загрузить историю"):
        try:
            response = requests.get(f"{BACKEND_URL}/history/{user_id}")

            if response.status_code == 200:
                data = response.json()

                if data['history']:
                    for item in data['history']:
                        with st.expander(f"📅 {item['date']}: {item['text'][:50]}..."):
                            st.write(f"**Продукты:** {item['text']}")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Калории", f"{data['calories']} ккал")
                        with col2:
                            st.metric("Белки", f"{data['protein']} г")
                        with col3:
                            st.metric("Жиры", f"{data['fat']} г")
                        with col4:
                            st.metric("Углеводы", f"{data['carbs']} г")
                else:
                    st.info("История пуста")
            else:
                st.error("Ошибка при загрузке истории")
        except Exception as e:
            st.error(f"Ошибка подключения: {str(e)}")

st.markdown("---")
st.markdown("### О проекте")
st.markdown(""" Это демонстрационная версия приложения для питания. Тут пока нет ЯндексДЖПТ""")