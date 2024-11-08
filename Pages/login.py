import hmac
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from streamlit_cookies_controller import CookieController
import jwt
import hashlib

def check_password():
    """Возвращает `True`, если пользователь авторизировался правильно."""
    global page_dict, conn

    def md5_(a):
        return hashlib.md5(a.encode()).hexdigest()

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
        cursor.execute(f"""INSERT INTO jwts (published, token, sysuser) VALUES ({"'" + str(JWTtime) + "'"}, {'"' + str(token) + '"'}, {sysuser})""")
        conn.commit()
        cursor.close()
        return token

    def password_entered():
        global conn
        cursor = conn.cursor()
        """Проверка на правильность введеного пароля"""
        @st.dialog("Ошибка авторизации")
        def incorrect_notice(text="Повторите попытку"):
            """Уведомление о неверном логине"""
            st.write(f"{text}")
            if st.button('Вернуться'):
                st.rerun()
        if '' in [st.session_state["username"],st.session_state["password"]]:
            incorrect_notice('Пустое поле ввода. Пожалуйста, введите пароль и логин.')
        else:
            print(str(md5_(st.session_state["username"] + st.secrets['keys']['splitter'] + st.session_state["password"])))
            if cursor.execute(f'SELECT COUNT(hash) FROM user WHERE login="{st.session_state["username"]}"').fetchone()[0]:
                
                if hmac.compare_digest(md5_(st.session_state["username"] + st.secrets['keys']['splitter'] + st.session_state["password"]), 
                                cursor.execute(f'SELECT hash FROM user WHERE login="{st.session_state["username"]}"').fetchone()[0]
                                ):
                    st.session_state["password_correct"] = True


                    #Задаем роль

                    #Для генерации токена
                    user = {"hash": st.session_state["hash"],
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
                    incorrect_notice('Не удалось авторизироваться. \nПожалуйста, повторите попытку.')
            else:
                st.session_state["password_correct"] = False
                incorrect_notice('Введённого Вами логина не существует. \nПожалуйста, повторите попытку авторизации.')
                return False
        

    # Возвращает True если логин и пароль верны.
    if st.session_state.get("password_correct", False):
        return True

    # Показывает введённые логин и пароль.
    login_form()
    if "password_correct" in st.session_state:
        st.error("Некорректные данные")
    return False

#секретный ключ для состания веб-токена
secret_key = st.secrets['keys']['secret_hash']
#время жизни веб токена в минутах
exp_time = 30

conn = sqlite3.connect('logs.db', check_same_thread=False)
if not check_password():
    st.stop()