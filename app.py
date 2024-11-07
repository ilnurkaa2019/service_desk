import streamlit as st
st.set_page_config(layout="wide")
import sqlite3
from streamlit_cookies_controller import CookieController
import jwt
from datetime import datetime

class tItems:
    def __init__(self):
        self.token = jwt.decode(bytes(controller.get('token'), 'utf-8'), secret_key, algorithms=['HS256'],
                                options={'verify_signature': False})
        self.login = self.token['user_id']['login']
        self.role = self.token['user_id']['role']
        self.exp = self.token['exp']

def delete_not_actual_tokens():
    global cursor
    id_n_tokens = cursor.execute("SELECT token FROM jwts").fetchall()
    for token in id_n_tokens:
        token=token[0]
        jwt_result = jwt.decode(bytes(token, 'utf-8'), secret_key, algorithms=['HS256'],
                                options={'verify_signature': False})

        if datetime.utcnow() > datetime.strptime(jwt_result['exp'], "%Y-%m-%d %H:%M:%S.%f"):
            cursor.execute(f'DELETE FROM jwts WHERE token="{token}"')

def autentification(conn):
    cursor = conn.cursor()
    def actual_tokens():
        token_in_db = []
        res = cursor.execute("SELECT token FROM jwts").fetchall()
        for token in res:
            token_in_db += [token[0]]
        return token_in_db
    token_in_web = controller.get('token')
    token_in_db = actual_tokens()
    if token_in_web in token_in_db:
        return True
    else:
        return False


def logout():
    if 'password_correct' in st.session_state:
        del st.session_state.password_correct
    if 'username' in st.session_state:
        del st.session_state['username']
    if cursor.execute(f"""SELECT COUNT(token) FROM jwts WHERE token="{controller.get('token')}" """):
        cursor.execute(f"""DELETE FROM jwts WHERE token="""
                       f"""(SELECT token FROM jwts j """
                       f"""LEFT JOIN user u ON j.sysuser=u.id """
                       f"""WHERE u.login="{tItems().login}" )""")
    controller.remove('token')
    st.rerun()


secret_key = 'jsONweBToken_secretKEy_ser_vi_ced_e_sk'
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()
controller = CookieController()
page_dict = []
delete_not_actual_tokens()
conn.commit()



if not autentification(conn):
    pg = st.navigation([st.Page(
        'Pages/login.py',
        title="Авторизация",
        url_path='/login',
        default=False)], position='hidden')
else:
    st.html('nav_bar.html')
    # Определеям страницы
    settings_ = st.Page(
        'Pages/settings.py',
        title="Настройки",
        url_path='/settings',
        default=False)
    a_stations_ = st.Page(
        'Pages/a_stations.py',
        title="Станции",
        url_path='/stations',
        default=False
    )
    empty_ = st.Page(
        'Pages/empty.py',
        title="Добро пожаловать")
    # Сортируем по ролям
    account_pages = [empty_, settings_]
    admin_pages = [a_stations_]

    if tItems().role == 'admin':
        page_dict = admin_pages
    pg = st.navigation(account_pages + page_dict, position='hidden')


pg.run()
conn.close()