import streamlit as st
import pandas as pd
from query_utils import run_query
from filters import date_filters, traffic_filters
from metrics import display_metrics
from charts import display_charts
from aggregations import display_aggregations

def show_dashboard(client):
    today = pd.to_datetime("today").date()
    yesterday = today - pd.Timedelta(days=1)
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)

    start_date, end_date = date_filters(today, yesterday, seven_days_ago, thirty_days_ago)

    # Converte as datas para string no formato 'YYYY-MM-DD' para a query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    table = st.session_state.username
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
    
    df = run_query(client, query)
    df_filtered = traffic_filters(df)

    display_metrics(df_filtered)
    display_charts(df_filtered)
    display_aggregations(df_filtered)

    query = f"""
    SELECT
        created_at `Horário`,
        transaction_id `ID da Transação`,
        first_name `Primeiro Nome`,
        status `Status`,
        value `Receita`,
        source `Origem`,
        medium `Mídia`,
        campaign `Campanha`,
        page_location `Página de Entrada`
    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    ORDER BY created_at DESC
    LIMIT 2000
    """

    df2 = run_query(client, query)

    st.header("Últimos Pedidos")
    st.data_editor(df2, hide_index=1, use_container_width=1)
