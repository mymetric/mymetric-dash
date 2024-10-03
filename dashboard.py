import streamlit as st
import pandas as pd
from query_handler import run_query
from filters import apply_filters, create_sidebar_filters
from charts import create_session_orders_chart
import os

is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'

cache_ttl = 6 if is_dev_mode else 600

def show_dashboard(client):
    # Configuração inicial de datas
    today = pd.to_datetime("today").date()
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)

    # Variáveis para definir os valores das datas
    start_date = seven_days_ago
    end_date = today

    with st.sidebar:
        st.markdown(f"## {st.session_state.username.upper()}")

    # Filtro de datas interativo
    with st.sidebar.expander("Seleção de Datas", expanded=True):
        if st.button("Hoje"):
            start_date = today
            end_date = today
        if st.button("Últimos 7 Dias"):
            start_date = seven_days_ago
            end_date = today
        if st.button("Últimos 30 Dias"):
            start_date = thirty_days_ago
            end_date = today
        start_date = st.date_input("Data Inicial", start_date)
        end_date = st.date_input("Data Final", end_date)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    table = st.session_state.username

    # Query para buscar os dados
    query = f"""
    SELECT
        event_date AS Data,
        source Origem,
        medium `Mídia`, 
        campaign Campanha,
        page_location `Página de Entrada`,
        COUNTIF(event_name = 'session') `Sessões`,
        COUNT(DISTINCT transaction_id) Pedidos,
        SUM(value) Receita,
        SUM(CASE WHEN status = 'paid' THEN value ELSE 0 END) `Receita Paga`
    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY ALL
    ORDER BY Pedidos DESC
    """
    rows = run_query(client, query)
    df = pd.DataFrame(rows)

    # Exibe o título do dashboard
    st.title("Visão Geral")

    # Criação de filtros
    df, origem_selected, midia_selected = create_sidebar_filters(df)

    # Exibir métricas
    pedidos = df["Pedidos"].sum()
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pedidos", f"{pedidos}")
    with col2:
        st.metric("Receita Capturada", f"R$ {total_receita_capturada:,.2f}")
    with col3:
        st.metric("Receita Paga", f"R$ {total_receita_paga:,.2f}")

    # Gráfico de Sessões e Pedidos
    create_session_orders_chart(df)

    # Exibe as tabelas
    st.data_editor(df.groupby(['Origem', 'Mídia']).sum().reset_index(), hide_index=1, use_container_width=1)
