import os
import json
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_location():
    """
    Obtém a localização baseada no IP usando o serviço ip-api.com
    """
    try:
        logger.info("Attempting to get location from ip-api.com")
        response = requests.get('http://ip-api.com/json/?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query')
        
        logger.info(f"IP API Response status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"IP API Response data: {data}")
            
            if data.get('status') == 'success':
                location_data = {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'ip': data.get('query', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0)
                }
                logger.info(f"Successfully retrieved location data: {location_data}")
                return location_data
            else:
                logger.error(f"IP API returned error status: {data.get('message', 'No message')}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to IP API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error getting location: {str(e)}")
    
    logger.warning("Returning default location data due to error")
    return {
        'city': 'Unknown',
        'region': 'Unknown',
        'country': 'Unknown',
        'ip': 'Unknown',
        'isp': 'Unknown',
        'timezone': 'Unknown',
        'lat': 0,
        'lon': 0
    }

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
    
    # Se for um evento de login, adiciona informações de localização
    if event_type == 'login':
        location = get_location()
        event_data = event_data or {}
        event_data.update(location)
    
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