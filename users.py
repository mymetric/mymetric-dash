# users.py

# Dicionário de usuários e senhas
# https://mymetric.streamlit.app
# usuário: evoke
# senha: asfGjHFzzAIwao8

import pandas as pd
import streamlit as st

# URL do CSV
csv_url = st.secrets["general"]["csv_url"]

# Lê o CSV da URL
df_google_sheet = pd.read_csv(csv_url)

# Converte o DataFrame em uma lista de dicionários
users = df_google_sheet.to_dict(orient='records')