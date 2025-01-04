import json
import os
from datetime import datetime

def load_table_metas(table_name):
    """
    Carrega as metas para uma tabela específica.
    Se o arquivo não existir, cria com valores padrão.
    """
    config_path = f'configs/{table_name}.json'
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Se o arquivo não existir, cria com valores padrão
        default_metas = {
            "metas_mensais": {
                datetime.now().strftime("%Y-%m"): {
                    "meta_receita_paga": 0
                }
            }
        }
        
        # Garante que a pasta configs existe
        os.makedirs('configs', exist_ok=True)
        
        # Salva o arquivo padrão
        with open(config_path, 'w') as f:
            json.dump(default_metas, f, indent=2)
        
        return default_metas

def save_table_metas(table_name, metas):
    """
    Salva as metas para uma tabela específica.
    """
    config_path = f'configs/{table_name}.json'
    
    # Garante que a pasta configs existe
    os.makedirs('configs', exist_ok=True)
    
    # Salva as metas
    with open(config_path, 'w') as f:
        json.dump(metas, f, indent=2) 