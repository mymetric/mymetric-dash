import os
import json
from datetime import datetime
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import requests

def get_location():
    """
    Obtém informações de localização do usuário através do IP.
    """
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': data.get('ip', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'user_agent': st.get_user_agent()
            }
    except:
        pass
    
    return {
        'ip': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'country': 'Unknown',
        'user_agent': st.get_user_agent()
    }

def get_bigquery_client():
    """Cria um cliente BigQuery com as credenciais corretas."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

def log_event(username, event_type, event_data=None):
    """
    Registra um evento do usuário no BigQuery.
    
    Args:
        username (str): Nome do usuário
        event_type (str): Tipo do evento (login, tab_view, etc)
        event_data (dict): Dados adicionais do evento
    """
    client = get_bigquery_client()
    
    # Se for um evento de login, adiciona informações de localização
    if event_type == 'login':
        location = get_location()
        event_data = event_data or {}
        event_data.update(location)
    
    # Converte o dicionário de dados para JSON
    event_data_json = json.dumps(event_data) if event_data else None
    
    # Query para inserir o evento
    query = f"""
    INSERT INTO `mymetric-hub-shopify.dbt_config.user_events`
    (username, event_type, event_data, created_at)
    VALUES
    ('{username}', '{event_type}', '{event_data_json}', CURRENT_TIMESTAMP())
    """
    
    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao registrar evento: {str(e)}")

def get_user_events(username):
    """
    Recupera todos os eventos de um usuário do BigQuery.
    
    Args:
        username (str): Nome do usuário
        
    Returns:
        list: Lista de eventos do usuário
    """
    client = get_bigquery_client()
    
    query = f"""
    SELECT
        event_type,
        event_data,
        FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%S', created_at) as timestamp
    FROM `mymetric-hub-shopify.dbt_config.user_events`
    WHERE username = '{username}'
    ORDER BY created_at DESC
    """
    
    try:
        df = client.query(query).to_dataframe()
        events = []
        for _, row in df.iterrows():
            event = {
                'event_type': row['event_type'],
                'timestamp': row['timestamp'],
                'data': json.loads(row['event_data']) if row['event_data'] else {}
            }
            events.append(event)
        return events
    except Exception as e:
        st.error(f"Erro ao recuperar eventos: {str(e)}")
        return []

def get_all_events():
    """
    Recupera eventos de todos os usuários do BigQuery.
    
    Returns:
        dict: Dicionário com eventos por usuário
    """
    client = get_bigquery_client()
    
    query = """
    SELECT
        username,
        event_type,
        event_data,
        FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%S', created_at) as timestamp
    FROM `mymetric-hub-shopify.dbt_config.user_events`
    ORDER BY created_at DESC
    """
    
    try:
        df = client.query(query).to_dataframe()
        events = {}
        for _, row in df.iterrows():
            username = row['username']
            if username not in events:
                events[username] = []
            
            event = {
                'event_type': row['event_type'],
                'timestamp': row['timestamp'],
                'data': json.loads(row['event_data']) if row['event_data'] else {}
            }
            events[username].append(event)
        return events
    except Exception as e:
        st.error(f"Erro ao recuperar eventos: {str(e)}")
        return {} 