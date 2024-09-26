import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

st.set_page_config(page_title="My App", page_icon=":bar_chart:", layout="wide")

# Cria o cliente da API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Função para executar a query
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return rows

# Filtro de datas interativo
st.sidebar.header("Filtro de Datas")

today = pd.to_datetime("today").date()

start_date = st.sidebar.date_input("Data Inicial", today)
end_date = st.sidebar.date_input("Data Final", today)

# Converte as datas para string no formato 'YYYY-MM-DD' para a query
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

table = st.query_params["table"]

# Query para buscar os dados com filtro de datas
query = f"""
SELECT
    source Origem,
    medium `Mídia`, 
    COUNTIF(event_name = 'session') `Sessões`,
    COUNT(DISTINCT transaction_id) Pedidos,
    SUM(value) Receita,
    SUM(CASE WHEN status = 'paid' THEN value ELSE 0 END) `Receita Paga`
FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
GROUP BY source, medium
ORDER BY Pedidos DESC
"""

# Executa a query
rows = run_query(query)

# Converte os dados em DataFrame para fácil manipulação
df = pd.DataFrame(rows)







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

# Exibe a tabela sem numeração
st.title("Visão Geral")

# Exibe a tabela de dados sem numeração
st.data_editor(df, hide_index=1, use_container_width=1)

