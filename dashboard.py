import streamlit as st
import pandas as pd
import pytz
from query_utils import run_query
from filters import date_filters, traffic_filters
from metrics import display_metrics
from charts import display_charts
from aggregations import display_aggregations
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

def show_dashboard(client, username):
    today = pd.to_datetime("today").date()
    yesterday = today - pd.Timedelta(days=1)
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)

    start_date, end_date = date_filters(today, yesterday, seven_days_ago, thirty_days_ago)

    # Converte as datas para string no formato 'YYYY-MM-DD' para a query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    table = username

    query1 = f"""
    SELECT
        event_date AS Data,
        source Origem,
        medium `Mídia`, 
        campaign Campanha,
        page_location `Página de Entrada`,
        COUNTIF(event_name = 'session') `Sessões`,
        
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' then transaction_id end) `Pedidos`,
        SUM(DISTINCT CASE WHEN event_name = 'purchase' then value end) `Receita`,

        COUNT(DISTINCT CASE WHEN event_name = 'purchase' and status = 'paid' THEN transaction_id END) `Pedidos Pagos`,
        SUM(CASE WHEN event_name = 'purchase' and status = 'paid' THEN value ELSE 0 END) `Receita Paga`,

        COUNT(DISTINCT CASE WHEN event_name = 'fs_purchase' then transaction_id end) `Pedidos PC`

    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY ALL
    ORDER BY Pedidos DESC
    """
    
    query2 = f"""
    SELECT
        created_at `Horário`,
        transaction_id `ID da Transação`,
        first_name `Primeiro Nome`,
        status `Status`,
        value `Receita`,
        source `Origem`,
        medium `Mídia`,
        campaign `Campanha`,
        page_location `Página de Entrada`,
        page_params `Parâmetros de URL`
    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
    WHERE date(created_at) BETWEEN '{start_date_str}' AND '{end_date_str}'
    ORDER BY created_at DESC
    LIMIT 2000
    """

    query3 = f"""
    SELECT
        round(count(distinct case when source = "not captured" then transaction_id end)/count(*), 4) `Taxa Perda de Cookies Hoje`
    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
    WHERE date(created_at) = current_date("America/Sao_Paulo")
    GROUP BY ALL
    """
    
    # Função auxiliar para rodar as queries
    def execute_query(query):
        return run_query(client, query)

    # Usar ThreadPoolExecutor para rodar as queries em paralelo
    with ThreadPoolExecutor() as executor:
        future_query1 = executor.submit(execute_query, query1)
        future_query2 = executor.submit(execute_query, query2)
        future_query3 = executor.submit(execute_query, query3)

        # Obter os resultados das queries
        df = future_query1.result()
        df2 = future_query2.result()
        df3 = future_query3.result()

    # Processar o resultado da terceira query
    tx_cookies = df3["Taxa Perda de Cookies Hoje"].sum()
    tx_cookies = tx_cookies * 100

    origem_options = ["Selecionar Todos"] + df['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + df['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + df['Campanha'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + df['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Fontes de Tráfego", expanded=False):
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    # Aplicar os filtros
    if "Selecionar Todos" in origem_selected:
        origem_selected = df['Origem'].unique().tolist()
    if "Selecionar Todos" in midia_selected:
        midia_selected = df['Mídia'].unique().tolist()
    if "Selecionar Todos" in campanha_selected:
        campanha_selected = df['Campanha'].unique().tolist()
    if "Selecionar Todos" in pagina_de_entrada_selected:
        pagina_de_entrada_selected = df['Página de Entrada'].unique().tolist()
    
    

    tab1, tab2 = st.tabs(["👀 Visão Geral", "🛒 Últimos Pedidos"])

    with tab1:
        df_filtered = traffic_filters(df, origem_selected, midia_selected, campanha_selected, pagina_de_entrada_selected)
        display_metrics(df_filtered, tx_cookies)
        display_charts(df_filtered)
        display_aggregations(df_filtered)

    with tab2:
        df_filtered2 = traffic_filters(df2, origem_selected, midia_selected, campanha_selected, pagina_de_entrada_selected)
        st.header("Últimos Pedidos")
        st.data_editor(df_filtered2, hide_index=1, use_container_width=1)
