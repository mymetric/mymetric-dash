import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
import dashboard  # Importa o arquivo de dashboard
from users import users  # Importa o dicionário de usuários e senhas

st.set_page_config(page_title="MyMetric HUB", page_icon=":bar_chart:", layout="wide")

# Logo URL
logo_url = "https://i.imgur.com/G5JAC2n.png"

# Display the header with the logo
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:center; padding:10px;">
        <img src="{logo_url}" alt="Logo" style="width:300px; height:90px; object-fit: cover;">
    </div>
    """,
    unsafe_allow_html=True
)

# Cria o cliente da API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Função de autenticação
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Formulário de login
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Usuário")
        password = st.sidebar.text_input("Senha", type="password")

        # Verifica se o nome de usuário e senha estão corretos
        if st.sidebar.button("Entrar"):
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()  # Recarrega a página após login
            else:
                st.sidebar.error("Usuário ou senha incorretos")
    
    return st.session_state.authenticated

# Função de logout
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None

# Executa a função de autenticação
if check_password():
    # O usuário está autenticado, carregue o dashboard
    dashboard.show_dashboard(client)

    # Adiciona o botão de logout na barra lateral
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()  # Recarrega a página após o logout
