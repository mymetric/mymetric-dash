import streamlit as st
import pandas as pd
import pytz

from query_utils import run_query
from filters import date_filters, traffic_filters
from metrics import display_metrics
from charts import display_charts
from aggregations import display_aggregations
from datetime import datetime, timedelta


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
        COUNT(DISTINCT CASE WHEN status = 'paid' THEN transaction_id END) `Pedidos Pagos`,
        SUM(value) Receita,
        SUM(CASE WHEN status = 'paid' THEN value ELSE 0 END) `Receita Paga`
    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY ALL
    ORDER BY Pedidos DESC
    """
    
    df = run_query(client, query)
    df_filtered = traffic_filters(df)

    

    query = f"""

    SELECT

    round(sum(case when source = "not captured" then 1 else 0 end)/count(*), 2) `Taxa Perda de Cookies Hoje`

    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`

    where

    date(created_at) = current_date("America/Sao_Paulo")
    
    group by all

    """
    df3 = run_query(client, query)
    tx_cookies = df3["Taxa Perda de Cookies Hoje"].sum()



    tab1, tab2 = st.tabs(["👀 Visão Geral", "🛒 Últimos Pedidos"])

    with tab1:
        display_metrics(df_filtered, tx_cookies)
        display_charts(df_filtered)
        display_aggregations(df_filtered)

    with tab2:
    
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
            page_location `Página de Entrada`,
            page_params `Parâmetros de URL`
        FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
        WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        ORDER BY created_at DESC
        LIMIT 2000
        """

        df2 = run_query(client, query)
        st.header("Últimos Pedidos")
        st.data_editor(df2, hide_index=1, use_container_width=1)





        # # Definir fuso horário de São Paulo
        # sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

        # # Calcular o horário atual no fuso horário de São Paulo, e depois remover o fuso horário para compatibilidade
        # current_time = pd.Timestamp.now(tz=sao_paulo_tz).tz_localize(None)
        # two_hours_ago = current_time - pd.Timedelta(hours=24)

        # # Converter a coluna 'Horário' para datetime, sem fuso horário
        # df2['Horário'] = pd.to_datetime(df2['Horário'])

        # # Obter o total de pedidos
        # total_pedidos = len(df2)

        # # Filtrar por 'Origem' igual a 'not captured'
        # df_filtered_origin = df2[df2['Origem'] == "not captured"]

        # # Obter o número de pedidos nas últimas 2 horas com 'Origem' igual a 'not captured'
        # df_last_two_hours = df_filtered_origin[df_filtered_origin['Horário'] >= two_hours_ago]
        # pedidos_not_captured_last_2h = len(df_last_two_hours)

        # # Calcular o total de pedidos nas últimas 2 horas
        # df_total_last_two_hours = df2[df2['Horário'] >= two_hours_ago]
        # total_pedidos_last_2h = len(df_total_last_two_hours)

        # # Calcular a taxa de 'not captured' sobre o total de pedidos
        # taxa_not_captured = (pedidos_not_captured_last_2h / total_pedidos_last_2h) * 100 if total_pedidos_last_2h > 0 else 0

        # # Exibir a taxa de 'not captured'
        # st.metric(label="Taxa % de 'not captured'", value=f"{pedidos_not_captured_last_2h:.2f}%")
        # st.metric(label="Taxa % de 'not captured'", value=f"{taxa_not_captured:.2f}%")