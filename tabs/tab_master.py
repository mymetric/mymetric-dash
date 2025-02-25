import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.load_data import load_internal_events
from modules.components import big_number_box

def display_tab_master():
    st.title("🧙🏻‍♂️ Master")

    # Carregar eventos internos
    df = load_internal_events()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('America/Sao_Paulo')
    
    # Filtrar apenas eventos de login
    df_logins = df[df['event_name'] == 'login']
    
    # Calcular MAU/WAU/DAU
    now = pd.Timestamp.now(tz='America/Sao_Paulo')
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    one_day_ago = now - timedelta(days=1)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mau = df_logins[df_logins['created_at'] >= thirty_days_ago]['user'].nunique()
        big_number_box(mau, "MAU", hint="Usuários únicos que fizeram login nos últimos 30 dias")
    
    with col2:
        wau = df_logins[df_logins['created_at'] >= seven_days_ago]['user'].nunique()
        big_number_box(wau, "WAU", hint="Usuários únicos que fizeram login nos últimos 7 dias")
    
    with col3:
        dau = df_logins[df_logins['created_at'] >= one_day_ago]['user'].nunique()
        big_number_box(dau, "DAU", hint="Usuários únicos que fizeram login nas últimas 24 horas")

    st.divider()
    
    # Análise por Tabela
    st.header("📊 Análise de Uso das Tabelas")
    
    # Filtrar usuários específicos para análise de tabelas
    df_tables = df[~df['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
    df_logins_tables = df_logins[~df_logins['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
    
    # Agrupar por tablename e calcular métricas
    table_analysis = (df_tables.groupby('tablename')
                     .agg({
                         'created_at': 'max',  # última atividade
                         'tab': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 abas mais acessadas
                         'event_name': 'count'  # total de eventos
                     })
                     .reset_index()
                     .rename(columns={'created_at': 'ultima_atividade'}))
    
    # Adicionar contagem de logins
    login_counts = df_logins_tables.groupby('tablename').size().reset_index(name='logins')
    table_analysis = table_analysis.merge(login_counts, on='tablename', how='left')
    table_analysis['logins'] = table_analysis['logins'].fillna(0).astype(int)
    
    # Ordenar por número de logins
    table_analysis = table_analysis.sort_values('logins', ascending=False)
    
    st.dataframe(
        table_analysis,
        column_config={
            "tablename": st.column_config.Column("📁 Nome da Tabela"),
            "logins": st.column_config.NumberColumn("🔑 Número de Logins", format="%d"),
            "event_name": st.column_config.NumberColumn("📊 Total de Eventos", format="%d"),
            "ultima_atividade": st.column_config.DatetimeColumn("⏰ Última Atividade", format="DD/MM/YY HH:mm"),
            "tab": st.column_config.Column("📑 Top 2 Abas")
        },
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # Análise por Usuário
    st.header("👤 Análise de Uso por Usuário")
    
    # Agrupar por usuário e calcular métricas
    user_analysis = (df.groupby('user')
                    .agg({
                        'created_at': 'max',  # última atividade
                        'tablename': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 tabelas mais acessadas
                        'tab': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 abas mais acessadas
                        'event_name': 'count'  # total de eventos
                    })
                    .reset_index()
                    .rename(columns={'created_at': 'ultima_atividade'}))
    
    # Adicionar contagem de logins
    user_login_counts = df_logins.groupby('user').size().reset_index(name='logins')
    user_analysis = user_analysis.merge(user_login_counts, on='user', how='left')
    user_analysis['logins'] = user_analysis['logins'].fillna(0).astype(int)
    
    # Ordenar por número de logins
    user_analysis = user_analysis.sort_values('logins', ascending=False)
    
    st.dataframe(
        user_analysis,
        column_config={
            "user": st.column_config.Column("👤 Usuário"),
            "logins": st.column_config.NumberColumn("🔑 Número de Logins", format="%d"),
            "event_name": st.column_config.NumberColumn("📊 Total de Eventos", format="%d"),
            "ultima_atividade": st.column_config.DatetimeColumn("⏰ Última Atividade", format="DD/MM/YY HH:mm"),
            "tablename": st.column_config.Column("📁 Top 2 Tabelas"),
            "tab": st.column_config.Column("📑 Top 2 Abas")
        },
        hide_index=True,
        use_container_width=True
    )

    st.divider()
    
    # Análise de Tabelas por Aba
    st.header("📑 Tabelas por Aba")
    
    # Contar tablenames distintos por aba
    tab_analysis = (df
                   .groupby('tab')
                   .agg({
                       'tablename': 'nunique',  # conta tablenames distintos
                       'event_name': 'count'    # total de eventos
                   })
                   .reset_index()
                   .rename(columns={
                       'tablename': 'tabelas_distintas',
                       'event_name': 'total_eventos'
                   })
                   .sort_values('tabelas_distintas', ascending=False))
    
    st.dataframe(
        tab_analysis,
        column_config={
            "tab": st.column_config.Column("📑 Aba"),
            "tabelas_distintas": st.column_config.NumberColumn("📁 Tabelas Distintas", format="%d"),
            "total_eventos": st.column_config.NumberColumn("📊 Total de Eventos", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )


    