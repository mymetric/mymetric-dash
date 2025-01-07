import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
import dashboard  # Importa o arquivo de dashboard
from users import users  # Importa o array de usuários e senhas
from datetime import datetime, timedelta
from helpers.components import send_discord_message
from analytics.logger import log_event, get_location

st.set_page_config(page_title="MyMetric HUB", page_icon=":bar_chart:", layout="wide")

# Logo URL
logo_url = "https://i.imgur.com/cPslqoR.png"

# Cria o cliente da API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Função de autenticação
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = None

    session_duration_days = 7  # Definir a duração da sessão em dias

    # Verifica se a sessão já expirou
    if st.session_state.authenticated:
        session_expiration_time = st.session_state.login_time + timedelta(days=session_duration_days)
        if datetime.now() > session_expiration_time:
            st.session_state.authenticated = False
            st.sidebar.warning("Sua sessão expirou. Faça login novamente.")
            st.session_state.login_time = None
            st.rerun()  # Recarrega a página após expiração

    if not st.session_state.authenticated:
        # Display the header with the logo
        st.sidebar.markdown(
            f"""
            <div>
                <img src="{logo_url}" alt="Logo" style="width:450px; height:90px; object-fit: cover;">
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Formulário de login
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Usuário")
        password = st.sidebar.text_input("Senha", type="password")

        # Verifica se o nome de usuário e senha estão corretos
        if st.sidebar.button("Entrar"):
            # Loop through the users list to check credentials
            for user in users:
                if user["slug"] == username and user["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now()  # Armazena o tempo do login
                    
                    # Obtém localização do usuário
                    location = get_location()
                    
                    # Registra o evento de login e envia mensagem para o Discord
                    log_event(username, 'login', {
                        'user_agent': st.session_state.get('user_agent', 'unknown'),
                        **location
                    })
                    
                    # Envia mensagem de login para o Discord
                    login_msg = f"""
🔐 **Novo Login no Dashboard**

**Usuário:** `{username}`
**Data/Hora:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`

**Localização do Acesso:**
> 🌆 Cidade: `{location['city']}`
> 🗺️ Estado: `{location['region']}`
> 🌎 País: `{location['country']}`
> 🌐 IP: `{location['ip']}`
> 📡 ISP: `{location['isp']}`
> 🕒 Timezone: `{location['timezone']}`
> 📍 Coords: `{location['lat']}, {location['lon']}`
"""
                    send_discord_message(login_msg)
                    
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
        user_names = [user["slug"] for user in users if user["slug"] != "mymetric"]

        # Display the header with the logo
        st.sidebar.markdown(
            f"""
            <div>
                <img src="{logo_url}" alt="Logo" style="width:450px; height:90px; object-fit: cover;">
            </div>
            """,
            unsafe_allow_html=True
        )

        selected_user = st.sidebar.selectbox("Escolha um usuário", options=user_names)
        st.sidebar.write(f"Selecionado: {selected_user}")
        # Exibe o dashboard como se o usuário selecionado estivesse autenticado
        dashboard.show_dashboard(client, selected_user)
    else:
        # Exibe o dashboard para o usuário autenticado
        dashboard.show_dashboard(client, st.session_state.username)

    # Adiciona o botão de logout na barra lateral
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()  # Recarrega a página após o logout