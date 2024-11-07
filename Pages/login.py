import hmac
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from streamlit_cookies_controller import CookieController
import jwt
def check_password():
    """Возвращает `True`, если пользователь авторизировался правильно."""
    global page_dict, conn

    def login_form():
        """Форма для сбора информации от пользователя"""
        st.header("Вход в систему")
        with st.form("Credentials"):
            st.text_input("Логин", key="username")
            st.text_input("Пароль", type="password", key="password")
            st.form_submit_button("Войти", on_click=password_entered)

    def generate_jwt_token(user_id, expiration_minutes):
        if user_id['role'] == 'admin':
            # Задаем время жизни токена
            expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            # Создаем словарь с данными пользователя, которые будут включены в токен
            payload = {
                "user_id": user_id,
                "exp": str(expiration_time)
            }
            # Генерируем JWT токен с помощью секретного ключа
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            return token

    #Добавление токена в db
    def add_JWT_to_db(conn, JWTtime, token, sysuser):
        cursor = conn.cursor()
        # try:
        cursor.execute(f"""INSERT INTO jwts (published, token, sysuser) VALUES ({"'" + str(JWTtime) + "'"}, {'"' + str(token) + '"'}, {sysuser})""")
        conn.commit()

        # except Exception as e:
        #     conn.rollback()
        #     return None
        # finally:
        cursor.close()
        return token

    def password_entered():
        """Проверка на правильность введеного пароля"""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True


            #Задаем роль

            #Для генерации токена
            user = {"login": st.session_state["username"],
                    "password": st.session_state["password"],
                    "role": conn.cursor().execute(f"""SELECT role FROM user WHERE login="{st.session_state["username"]}" """).fetchone()[0]}
            token = generate_jwt_token(user, exp_time)
            sysuser = conn.cursor().execute(f"""SELECT id FROM user WHERE login ="{user['login']}" """).fetchone()[0]
            add_JWT_to_db(conn, datetime.utcnow(), token, sysuser)
            controller = CookieController()
            controller.set('token', token)
            st.session_state.token = token
            del st.session_state["password"]  # Не храним пароль и логин в состоянии страницы
            # del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Возвращает True если логин и пароль верны.
    if st.session_state.get("password_correct", False):
        return True

    # Показывает введённые логин и пароль.
    login_form()
    if "password_correct" in st.session_state:
        st.error("Логин или пароль введены неправильно")
    return False

#секретный ключ для состания веб-токена
secret_key = "jsONweBToken_secretKEy_ser_vi_ced_e_sk"
#время жизни веб токена в минутах
exp_time = 30

conn = sqlite3.connect('logs.db', check_same_thread=False)
if not check_password():
    st.stop()