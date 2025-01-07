import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from helpers.components import run_query, section_title, big_number_box

def display_tab_master(client):
    st.header("Painel Mestre")
    
    # Query para métricas gerais
    query_metrics = """
    WITH user_activity AS (
        SELECT
            username,
            COUNT(*) as total_events,
            COUNT(DISTINCT DATE(created_at)) as days_active,
            MIN(created_at) as first_activity,
            MAX(created_at) as last_activity,
            CURRENT_TIMESTAMP() as now
        FROM `mymetric-hub-shopify.dbt_config.user_events`
        GROUP BY username
    )
    SELECT
        COUNT(DISTINCT username) as total_users,
        COUNTIF(DATE(last_activity) = CURRENT_DATE()) as active_today,
        COUNTIF(DATE_DIFF(CURRENT_DATE(), DATE(last_activity), DAY) <= 7) as active_7d,
        COUNTIF(DATE_DIFF(CURRENT_DATE(), DATE(last_activity), DAY) <= 30) as active_30d,
        AVG(days_active) as avg_active_days,
        AVG(total_events) as avg_events_per_user
    FROM user_activity
    """
    
    # Query para análise por usuário
    query_user_metrics = """
    WITH event_counts AS (
        SELECT
            username,
            COUNT(*) as total_events,
            COUNTIF(event_type = 'login') as login_count,
            COUNTIF(event_type = 'tab_view') as tab_views,
            MIN(created_at) as first_activity,
            MAX(created_at) as last_activity
        FROM `mymetric-hub-shopify.dbt_config.user_events`
        GROUP BY username
    )
    SELECT
        username as usuario,
        total_events as total_eventos,
        login_count as logins,
        tab_views as views_abas,
        FORMAT_TIMESTAMP('%d/%m/%Y %H:%M', first_activity) as primeira_atividade,
        FORMAT_TIMESTAMP('%d/%m/%Y %H:%M', last_activity) as ultima_atividade,
        DATE_DIFF(last_activity, first_activity, DAY) + 1 as dias_uso
    FROM event_counts
    ORDER BY total_events DESC
    """
    
    # Query para abas mais visitadas
    query_tab_views = """
    WITH tab_data AS (
        SELECT
            JSON_EXTRACT_SCALAR(event_data, '$.tab') as tab_name
        FROM `mymetric-hub-shopify.dbt_config.user_events`
        WHERE event_type = 'tab_view'
        AND event_data IS NOT NULL
    )
    SELECT
        IFNULL(tab_name, 'unknown') as aba,
        COUNT(*) as visualizacoes
    FROM tab_data
    GROUP BY tab_name
    ORDER BY visualizacoes DESC
    """
    
    # Query para últimos logins
    query_logins = """
    SELECT
        username as usuario,
        FORMAT_TIMESTAMP('%d/%m/%Y %H:%M', created_at) as data_hora,
        JSON_EXTRACT_SCALAR(event_data, '$.city') as cidade,
        JSON_EXTRACT_SCALAR(event_data, '$.region') as estado,
        JSON_EXTRACT_SCALAR(event_data, '$.country') as pais,
        JSON_EXTRACT_SCALAR(event_data, '$.ip') as ip,
        JSON_EXTRACT_SCALAR(event_data, '$.user_agent') as user_agent
    FROM `mymetric-hub-shopify.dbt_config.user_events`
    WHERE event_type = 'login'
    AND event_data IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 1000
    """
    
    # Executa as queries
    df_metrics = run_query(client, query_metrics)
    df_user_metrics = run_query(client, query_user_metrics)
    df_tab_views = run_query(client, query_tab_views)
    df_logins = run_query(client, query_logins)
    
    # Renomeia as colunas para exibição
    df_user_metrics = df_user_metrics.rename(columns={
        'usuario': 'Usuário',
        'total_eventos': 'Total de Eventos',
        'logins': 'Logins',
        'views_abas': 'Views de Abas',
        'primeira_atividade': 'Primeira Atividade',
        'ultima_atividade': 'Última Atividade',
        'dias_uso': 'Dias de Uso'
    })
    
    df_tab_views = df_tab_views.rename(columns={
        'aba': 'Aba',
        'visualizacoes': 'Visualizações'
    })
    
    df_logins = df_logins.rename(columns={
        'usuario': 'Usuário',
        'data_hora': 'Data/Hora',
        'cidade': 'Cidade',
        'estado': 'Estado',
        'pais': 'País',
        'ip': 'IP',
        'user_agent': 'User Agent'
    })
    
    # Exibe métricas gerais
    section_title("📊 Métricas de Uso")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"{int(df_metrics['total_users'].iloc[0]):,}".replace(",", "."),
            "Total de Usuários",
            hint="Número total de usuários registrados no sistema"
        )
    
    with col2:
        big_number_box(
            f"{int(df_metrics['active_today'].iloc[0]):,}".replace(",", "."),
            "Ativos Hoje",
            hint="Usuários que realizaram alguma ação hoje"
        )
    
    with col3:
        big_number_box(
            f"{int(df_metrics['active_7d'].iloc[0]):,}".replace(",", "."),
            "Ativos (7d)",
            hint="Usuários que realizaram alguma ação nos últimos 7 dias"
        )
    
    with col4:
        big_number_box(
            f"{int(df_metrics['active_30d'].iloc[0]):,}".replace(",", "."),
            "Ativos (30d)",
            hint="Usuários que realizaram alguma ação nos últimos 30 dias"
        )
    
    # Métricas de engajamento
    section_title("🎯 Engajamento")
    col1, col2 = st.columns(2)
    
    with col1:
        big_number_box(
            f"{df_metrics['avg_active_days'].iloc[0]:.1f}",
            "Média de Dias Ativos",
            hint="Média de dias que os usuários acessam o sistema"
        )
    
    with col2:
        big_number_box(
            f"{df_metrics['avg_events_per_user'].iloc[0]:.1f}",
            "Média de Eventos/Usuário",
            hint="Média de ações realizadas por usuário"
        )
    
    # Análise por Usuário
    section_title("👥 Análise por Usuário")
    st.dataframe(df_user_metrics, hide_index=True, use_container_width=True)
    
    # Análise de Abas mais Visitadas
    section_title("📑 Abas mais Visitadas")
    st.dataframe(df_tab_views, hide_index=True, use_container_width=True)
    
    # Análise de Logins
    section_title("🔐 Últimos Logins")
    st.dataframe(df_logins, hide_index=True, use_container_width=True) 