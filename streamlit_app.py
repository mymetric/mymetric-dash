import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
import dashboard  # Importa o arquivo de dashboard
from users import users  # Importa o array de usuários e senhas
from datetime import datetime, timedelta
from helpers.components import send_discord_message
from analytics.logger import log_event
from pathlib import Path
import base64

st.set_page_config(
    page_title="MyMetricHUB",
    page_icon="https://mymetric.com.br/wp-content/uploads/2023/07/cropped-Novo-Logo-Icone-32x32.jpg",
    layout="wide"
)

# Logo path
logo_path = Path(__file__).parent / "logo.svg"
with open(logo_path, "rb") as f:
    logo_contents = f.read()

# Cria o cliente da API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Função de autenticação
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.login_time = None
    elif st.session_state.login_time:
        # Verifica se o login ainda é válido (7 dias)
        if datetime.now() - st.session_state.login_time < timedelta(days=7):
            return True
        else:
            # Reseta a sessão se expirou
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.login_time = None

    # Sempre mostra o logo
    st.sidebar.markdown(
        f"""
        <div>
            <img src="data:image/svg+xml;base64,{base64.b64encode(logo_contents).decode()}" alt="Logo" style="width: 250px;height: 75px;object-fit: cover;margin: 0 auto;display: block;">
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.authenticated:
        username = st.sidebar.text_input("Usuário")
        password = st.sidebar.text_input("Senha", type="password")
        
        if st.sidebar.button("Entrar"):
            # Loop through the users list to check credentials
            for user in users:
                if user["slug"] == username and user["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now()  # Armazena o tempo do login
                    
                    # Registra o evento de login
                    log_event(username, 'login')
                    
                    # Envia alerta de login para o Discord
                    login_alert = {
                        'titulo': 'Nova Sessão Iniciada',
                        'descricao': f'O cliente **{username}** iniciou uma nova sessão no dashboard.',
                        'acao': f'Sessão iniciada em {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}',
                        'severidade': 'baixa'
                    }
                    from helpers.notices import send_discord_alert
                    send_discord_alert(login_alert, username)
                    
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

# Executa a função de autenticação
if check_password():
    # Verifica se o usuário é 'mymetric' (usuário mestre)
    if st.session_state.username == "mymetric":
        # Gera um dropdown para escolher outros usuários
        with st.sidebar.expander("Conta Mestre", expanded=True):
            user_names = [user["slug"] for user in users if user["slug"] not in ["mymetric", "buildgrowth", "alvisi"]]
            selected_user = st.selectbox("Escolha", options=user_names)
            st.write(f"Selecionado: {selected_user}")
            # Exibe o dashboard como se o usuário selecionado estivesse autenticado
        dashboard.show_dashboard(client, selected_user)
    elif st.session_state.username == "buildgrowth":
        # Gera um dropdown para escolher entre holysoup e orthocrin
        with st.sidebar.expander("Conta MCC", expanded=True):
            client_options = ["holysoup", "orthocrin"]
            selected_client = st.selectbox("Escolha o cliente", options=client_options)
            st.write(f"Cliente selecionado: {selected_client}")
        dashboard.show_dashboard(client, selected_client)
    elif st.session_state.username == "alvisi":
        # Gera um dropdown para escolher entre holysoup e orthocrin
        with st.sidebar.expander("Conta MCC", expanded=True):
            client_options = ["holysoup", "coffeemais"]
            selected_client = st.selectbox("Escolha o cliente", options=client_options)
            st.write(f"Cliente selecionado: {selected_client}")
        dashboard.show_dashboard(client, selected_client)
    else:
        # Exibe o dashboard para o usuário autenticado
        dashboard.show_dashboard(client, st.session_state.username)

    # Adiciona o botão de logout na barra lateral
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()  # Recarrega a página após o logout