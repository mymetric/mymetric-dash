import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from helpers.components import run_query
from analytics.logger import get_all_events

def display_tab_master(client):
    st.header("Painel Mestre")
    
    # Busca todos os eventos
    all_events = get_all_events()
    
    # Métricas Gerais
    st.subheader("Métricas de Uso")
    
    # Calcula métricas gerais
    total_users = len(all_events)
    total_events = sum(len(events) for events in all_events.values())
    
    # Usuários ativos
    now = datetime.now()
    active_today = 0
    active_7d = 0
    active_30d = 0
    
    for user_events in all_events.values():
        if not user_events:
            continue
            
        last_event = datetime.fromisoformat(user_events[-1]['timestamp'])
        if last_event.date() == now.date():
            active_today += 1
        if (now - last_event) <= timedelta(days=7):
            active_7d += 1
        if (now - last_event) <= timedelta(days=30):
            active_30d += 1
    
    # Exibe métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Usuários", total_users)
    
    with col2:
        st.metric("Ativos Hoje", active_today)
    
    with col3:
        st.metric("Ativos (7d)", active_7d)
    
    with col4:
        st.metric("Ativos (30d)", active_30d)
    
    # Análise por Usuário
    st.subheader("Análise por Usuário")
    
    user_metrics = []
    for username, events in all_events.items():
        if not events:
            continue
            
        # Conta eventos por tipo
        event_types = {}
        for event in events:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Calcula primeira e última atividade
        first_event = datetime.fromisoformat(events[0]['timestamp'])
        last_event = datetime.fromisoformat(events[-1]['timestamp'])
        
        user_metrics.append({
            'Usuário': username,
            'Total de Eventos': len(events),
            'Logins': event_types.get('login', 0),
            'Views de Abas': event_types.get('tab_view', 0),
            'Primeira Atividade': first_event.strftime('%d/%m/%Y %H:%M'),
            'Última Atividade': last_event.strftime('%d/%m/%Y %H:%M'),
            'Dias de Uso': (last_event - first_event).days + 1
        })
    
    # Cria DataFrame e ordena por total de eventos
    df_metrics = pd.DataFrame(user_metrics)
    if not df_metrics.empty:
        df_metrics = df_metrics.sort_values('Total de Eventos', ascending=False)
        st.dataframe(df_metrics, hide_index=True, use_container_width=True)
    
    # Análise de Abas mais Visitadas
    st.subheader("Abas mais Visitadas")
    
    tab_views = {}
    for events in all_events.values():
        for event in events:
            if event['event_type'] == 'tab_view':
                tab_name = event['data'].get('tab', 'unknown')
                tab_views[tab_name] = tab_views.get(tab_name, 0) + 1
    
    if tab_views:
        df_tabs = pd.DataFrame([
            {'Aba': tab, 'Visualizações': views}
            for tab, views in tab_views.items()
        ]).sort_values('Visualizações', ascending=False)
        
        st.dataframe(df_tabs, hide_index=True, use_container_width=True)
    
    # Análise de Logins
    st.subheader("Últimos Logins")
    
    login_data = []
    for username, events in all_events.items():
        for event in events:
            if event['event_type'] == 'login':
                login_data.append({
                    'Usuário': username,
                    'Data/Hora': datetime.fromisoformat(event['timestamp']).strftime('%d/%m/%Y %H:%M'),
                    'Cidade': event['data'].get('city', 'Unknown'),
                    'Estado': event['data'].get('region', 'Unknown'),
                    'País': event['data'].get('country', 'Unknown'),
                    'IP': event['data'].get('ip', 'Unknown'),
                    'User Agent': event['data'].get('user_agent', 'Unknown')
                })
    
    if login_data:
        df_logins = pd.DataFrame(login_data)
        df_logins = df_logins.sort_values('Data/Hora', ascending=False)
        st.dataframe(df_logins, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum login registrado ainda.") 