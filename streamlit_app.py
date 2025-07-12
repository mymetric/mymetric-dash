import streamlit as st
st.set_page_config(
    page_title="MyMetricHUB",
    page_icon="https://mymetric.com.br/wp-content/uploads/2023/07/cropped-Novo-Logo-Icone-32x32.jpg",
    layout="wide"
)

import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
from core.users import load_users
from datetime import datetime, timedelta
from pathlib import Path
import base64
from core.app import load_app
from modules.utilities import send_message
from modules.load_data import load_all_users, save_event_name
from streamlit_cookies_controller import CookieController
import pytz

# Adiciona fonte e estilos globais
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 15px;
            letter-spacing: -0.01em;
        }

        h1 {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 600;
            font-size: 32px !important;
            letter-spacing: -0.02em;
            margin-bottom: 16px !important;
        }

        h2 {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 600;
            font-size: 24px !important;
            letter-spacing: -0.02em;
            margin-bottom: 14px !important;
        }

        h3 {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 600;
            font-size: 20px !important;
            letter-spacing: -0.02em;
            margin-bottom: 12px !important;
        }

        .stButton button {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 500;
            font-size: 15px !important;
        }

        .stSelectbox div div div {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 15px !important;
        }

        /* Aumenta o tamanho do texto em inputs e seletores */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            font-size: 15px !important;
        }

        /* Aumenta o tamanho do texto em tabelas */
        .dataframe {
            font-size: 15px !important;
        }

        /* Aumenta o tamanho do texto em métricas */
        .metric-value {
            font-size: 16px !important;
        }

        /* Ajusta o tamanho do texto em expanders */
        .streamlit-expanderHeader {
            font-size: 15px !important;
        }

        /* Ajusta o tamanho do texto em radio buttons e checkboxes */
        .stRadio label, .stCheckbox label {
            font-size: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Carrega estilos adicionais para botões
with open('assets/button_styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# def get_cookies():
controller = CookieController()
authenticated = controller.get("mm_authenticated")
if authenticated:
    st.session_state.authenticated = authenticated
    st.session_state.username = controller.get("mm_username")
    st.session_state.tablename = controller.get("mm_tablename")
    st.session_state.admin = controller.get("mm_admin")



# Logo path
logo_path = Path(__file__).parent / "images/logo.svg"
with open(logo_path, "rb") as f:
    logo_contents = f.read()

# Add hover style for logo
st.markdown("""
    <style>
        .logo {
            transition: filter 0.5s ease;
        }
        .logo:hover {
            filter: invert(27%) sepia(51%) saturate(2878%) hue-rotate(346deg) brightness(104%) contrast(97%);
        }
    </style>
""", unsafe_allow_html=True)

# Sempre mostra o logo
st.sidebar.markdown(
    f"""
    <div>
        <img class="logo" src="data:image/svg+xml;base64,{base64.b64encode(logo_contents).decode()}" alt="Logo" style="width: 250px;height: 75px;object-fit: cover;margin: 0 auto;display: block;">
    </div>
    """,
    unsafe_allow_html=True
)


# Função de autenticação
def check_password():
    
    if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.login_time = None
            st.session_state.tablename = None
            st.session_state.admin = None

    if not st.session_state.authenticated:
        # Adicionar CSS para melhorar autopreenchimento
        st.markdown("""
            <style>
                /* Melhorar autopreenchimento do Chrome */
                .stTextInput input:-webkit-autofill,
                .stTextInput input:-webkit-autofill:hover,
                .stTextInput input:-webkit-autofill:focus,
                .stTextInput input:-webkit-autofill:active {
                    -webkit-box-shadow: 0 0 0 30px white inset !important;
                    -webkit-text-fill-color: #31333F !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Formulário HTML oculto para ajudar o Chrome a reconhecer os campos
        st.sidebar.markdown("""
            <form id="hidden-login-form" style="display: none;">
                <input type="text" name="username" autocomplete="username">
                <input type="password" name="current-password" autocomplete="current-password">
            </form>
        """, unsafe_allow_html=True)
        
        # Formulário Streamlit com melhorias para autopreenchimento
        with st.sidebar.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuário", key="username_input", autocomplete="username")
            password = st.text_input("Senha", type="password", key="password_input", autocomplete="current-password")
            submit_button = st.form_submit_button("Entrar", type="primary")

        users = load_users()
        new_users = load_all_users()
        new_users = new_users.to_dict(orient="records")
        

        if submit_button:
            # Loop through the users list to check credentials
            for user in users:
                if user["slug"] == username and user["password"] == password:
                    
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.tablename = username
                    st.session_state.admin = True
                    st.session_state.login_time = datetime.now()  # Armazena o tempo do login
                    
                    save_event_name(event_name="login", event_params={})
                    
                    if username != "mymetric":
                        send_message(f"🔐 Novo login detectado!\n\nUsuário: {username}\nData/Hora: {datetime.now().astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}")

                    st.rerun()  # Recarrega a página após login
                    break
            
            for user in new_users:
                
                encoded_password = base64.b64encode(password.encode()).decode()
                
                if user["email"] == username and user["password"] == encoded_password:
                    expires_at = datetime.now() + timedelta(days=1)
                    
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.tablename = user["tablename"]
                    st.session_state.admin = user["admin"]
                    st.session_state.login_time = datetime.now()  # Armazena o tempo do login

                    save_event_name(event_name="login", event_params={})
                    
                    if username != "mymetric":
                        send_message(f"🔐 Novo login detectado!\n\nUsuário: {username}\nData/Hora: {datetime.now().astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}")

                    
                    st.rerun()  # Recarrega a página após login
                    break
            else:
                st.sidebar.error("Usuário ou senha incorretos")
    
    return st.session_state.authenticated

# Função de logout
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None

    controller = CookieController()
    controller.remove("mm_authenticated")
    controller.remove("mm_username")
    controller.remove("mm_tablename")
    controller.remove("mm_admin")

# Executa a função de autenticação
if check_password():
    # Verifica se o usuário é 'mymetric' (usuário mestre)
    if st.session_state.username == "mymetric" or st.session_state.username == "alvisi":
        # Gera um dropdown para escolher outros usuários
        with st.sidebar.expander("Conta Mestre", expanded=True):
            users = load_users()
            user_names = [user["slug"] for user in users if user["slug"] not in ["mymetric", "buildgrowth", "alvisi"]]
            selected_user = st.selectbox("Escolha", options=user_names, index=None)
            # st.write(f"Selecionado: {selected_user}")
            st.session_state.tablename = selected_user
            st.session_state.admin = True  # Garantir que admin permanece True para usuário mymetric
            # Exibe o dashboard como se o usuário selecionado estivesse autenticado
        if selected_user:
            load_app()
    elif st.session_state.username == "buildgrowth":
        # Gera um dropdown para escolher entre holysoup e orthocrin
        with st.sidebar.expander("Conta MCC", expanded=True):
            client_options = ["holysoup", "orthocrin"]
            selected_client = st.selectbox("Escolha o cliente", options=client_options)
            st.write(f"Cliente selecionado: {selected_client}")
            st.session_state.tablename = selected_client
        load_app()
    elif st.session_state.username == "alvisi":
        # Gera um dropdown para escolher entre holysoup e orthocrin
        with st.sidebar.expander("Conta MCC", expanded=True):
            client_options = ["holysoup", "coffeemais", "3dfila"]
            selected_client = st.selectbox("Escolha o cliente", options=client_options)
            st.write(f"Cliente selecionado: {selected_client}")
            st.session_state.tablename = selected_client
            st.session_state.admin = True  # Garantir que admin permanece True para usuário alvisi
        load_app()
    else:
        # Exibe o dashboard para o usuário autenticado
        load_app()

    # Adiciona o botão de logout na barra lateral
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()  # Recarrega a página após o logout
        
