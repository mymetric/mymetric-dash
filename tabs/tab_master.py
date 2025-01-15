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
            COUNT(DISTINCT DATE(created_at, 'America/Sao_Paulo')) as days_active,
            MIN(created_at) as first_activity,
            MAX(created_at) as last_activity,
            CURRENT_TIMESTAMP() as now
        FROM `mymetric-hub-shopify.dbt_config.user_events`
        GROUP BY username
    )
    SELECT
        COUNT(DISTINCT username) as total_users,
        COUNTIF(DATE(last_activity, 'America/Sao_Paulo') = CURRENT_DATE('America/Sao_Paulo')) as active_today,
        COUNTIF(DATE_DIFF(CURRENT_DATE('America/Sao_Paulo'), DATE(last_activity, 'America/Sao_Paulo'), DAY) <= 7) as active_7d,
        COUNTIF(DATE_DIFF(CURRENT_DATE('America/Sao_Paulo'), DATE(last_activity, 'America/Sao_Paulo'), DAY) <= 30) as active_30d,
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
    ),
    tab_preferences AS (
        SELECT 
            username,
            JSON_EXTRACT_SCALAR(event_data, '$.tab') as tab_name,
            COUNT(*) as tab_views
        FROM `mymetric-hub-shopify.dbt_config.user_events`
        WHERE event_type = 'tab_view'
        AND event_data IS NOT NULL
        AND LOWER(JSON_EXTRACT_SCALAR(event_data, '$.tab')) != 'visao_geral'
        GROUP BY username, tab_name
    ),
    most_viewed_tab AS (
        SELECT
            username,
            ARRAY_AGG(STRUCT(tab_name, tab_views) ORDER BY tab_views DESC LIMIT 1)[OFFSET(0)].tab_name as favorite_tab
        FROM tab_preferences
        GROUP BY username
    )
    SELECT
        e.username as usuario,
        e.total_events as total_eventos,
        e.login_count as logins,
        e.tab_views as views_abas,
        FORMAT_TIMESTAMP('%d/%m/%Y %H:%M', e.first_activity, 'America/Sao_Paulo') as primeira_atividade,
        FORMAT_TIMESTAMP('%d/%m/%Y %H:%M', e.last_activity, 'America/Sao_Paulo') as ultima_atividade,
        DATE_DIFF(e.last_activity, e.first_activity, DAY) + 1 as dias_uso,
        IFNULL(t.favorite_tab, 'N/A') as aba_favorita
    FROM event_counts e
    LEFT JOIN most_viewed_tab t ON e.username = t.username
    ORDER BY e.last_activity DESC
    """
    
    # Executa as queries
    df_metrics = run_query(client, query_metrics)
    df_user_metrics = run_query(client, query_user_metrics)
    
    # Renomeia as colunas para exibição
    df_user_metrics = df_user_metrics.rename(columns={
        'usuario': 'Usuário',
        'total_eventos': 'Total de Eventos',
        'logins': 'Logins',
        'views_abas': 'Views de Abas',
        'primeira_atividade': 'Primeira Atividade',
        'ultima_atividade': 'Última Atividade',
        'dias_uso': 'Dias de Uso',
        'aba_favorita': 'Aba Favorita'
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