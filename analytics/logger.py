import os
import json
from datetime import datetime

def log_event(username, event_type, event_data=None):
    """
    Registra um evento do usuário em um arquivo JSON.
    
    Args:
        username (str): Nome do usuário
        event_type (str): Tipo do evento (login, tab_view, etc)
        event_data (dict): Dados adicionais do evento
    """
    
    # Cria o diretório analytics/logs se não existir
    os.makedirs('analytics/logs', exist_ok=True)
    
    # Nome do arquivo de log para este usuário
    log_file = f'analytics/logs/{username}.json'
    
    # Prepara o evento
    event = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'data': event_data or {}
    }
    
    # Carrega eventos existentes ou cria lista vazia
    try:
        with open(log_file, 'r') as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []
    
    # Adiciona novo evento
    events.append(event)
    
    # Salva todos os eventos
    with open(log_file, 'w') as f:
        json.dump(events, f, indent=2)

def get_user_events(username):
    """
    Recupera todos os eventos de um usuário.
    
    Args:
        username (str): Nome do usuário
        
    Returns:
        list: Lista de eventos do usuário
    """
    log_file = f'analytics/logs/{username}.json'
    
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_all_events():
    """
    Recupera eventos de todos os usuários.
    
    Returns:
        dict: Dicionário com eventos por usuário
    """
    events = {}
    logs_dir = 'analytics/logs'
    
    if not os.path.exists(logs_dir):
        return events
        
    for filename in os.listdir(logs_dir):
        if filename.endswith('.json'):
            username = filename[:-5]  # remove .json
            events[username] = get_user_events(username)
            
    return events 