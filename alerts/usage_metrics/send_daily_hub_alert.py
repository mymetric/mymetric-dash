#!/usr/bin/env python3
"""
Script para envio automático do alerta diário de uso do hub.
Este script pode ser executado via cron job para enviar alertas diários.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

# Importar o módulo de alertas
from hub_daily_usage import send_alerts_to_test_groups, send_daily_hub_usage_alert

def load_config():
    """Carrega configurações do arquivo de configuração."""
    config_file = os.path.join(current_dir, 'alert_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {str(e)}")
            return None
    else:
        # Configuração padrão
        default_config = {
            "test_groups": [
                "5511999999999-1234567890"  # Substitua pelo ID real do grupo de teste
            ],
            "admin_phone": "5511999999999",  # Substitua pelo seu número
            "enable_daily_alerts": True,
            "enable_test_mode": False
        }
        
        # Salvar configuração padrão
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 Arquivo de configuração criado: {config_file}")
            print("⚠️ Por favor, edite o arquivo com os números corretos antes de usar.")
            return default_config
        except Exception as e:
            print(f"❌ Erro ao criar arquivo de configuração: {str(e)}")
            return None

def send_daily_alert():
    """Envia o alerta diário de uso do hub."""
    print(f"🚀 Iniciando envio do alerta diário - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração
    config = load_config()
    if not config:
        print("❌ Falha ao carregar configuração")
        return False
    
    if not config.get("enable_daily_alerts", True):
        print("⚠️ Alertas diários desabilitados na configuração")
        return True
    
    test_mode = config.get("enable_test_mode", False)
    
    try:
        # Enviar para grupos de teste
        success = send_alerts_to_test_groups(test_mode=test_mode)
        
        if success:
            print("✅ Alertas enviados com sucesso para todos os grupos!")
            
            # Enviar confirmação para admin se configurado
            admin_phone = config.get("admin_phone")
            if admin_phone and admin_phone != "5511999999999":
                confirmation_message = f"""
✅ *ALERTA DIÁRIO ENVIADO*
📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

O alerta de uso diário do hub foi enviado com sucesso para todos os grupos configurados.

🔗 *ACESSO AO HUB*
https://mymetric-hub.streamlit.app
"""
                send_daily_hub_usage_alert(admin_phone, testing_mode=False)
                print(f"✅ Confirmação enviada para admin: {admin_phone}")
            
            return True
        else:
            print("❌ Falha ao enviar alertas para alguns grupos")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o envio do alerta: {str(e)}")
        return False

def main():
    """Função principal do script."""
    print("📊 SISTEMA DE ALERTAS DIÁRIOS - MYMETRIC HUB")
    print("=" * 50)
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # Modo teste
            print("🧪 Executando em modo teste...")
            config = load_config()
            if config:
                config["enable_test_mode"] = True
                success = send_daily_alert()
                print(f"✅ Teste {'concluído com sucesso' if success else 'falhou'}")
                return 0 if success else 1
        
        elif command == "config":
            # Mostrar configuração atual
            config = load_config()
            if config:
                print("📋 Configuração atual:")
                print(json.dumps(config, indent=2))
                return 0
            else:
                print("❌ Falha ao carregar configuração")
                return 1
        
        elif command == "help":
            # Mostrar ajuda
            print("""
📖 AJUDA - SISTEMA DE ALERTAS DIÁRIOS

Uso: python send_daily_hub_alert.py [comando]

Comandos disponíveis:
  (sem comando)  - Envia alerta diário normal
  test           - Envia alerta em modo teste
  config         - Mostra configuração atual
  help           - Mostra esta ajuda

Configuração:
  O arquivo alert_config.json é criado automaticamente na primeira execução.
  Edite este arquivo para configurar os números de WhatsApp e outras opções.

Cron Job (para envio automático diário):
  0 18 * * * cd /caminho/para/projeto && python send_daily_hub_alert.py
            """)
            return 0
        
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("Execute 'python send_daily_hub_alert.py help' para ver os comandos disponíveis")
            return 1
    
    # Execução normal (sem argumentos)
    success = send_daily_alert()
    
    if success:
        print("\n🎉 Alerta diário enviado com sucesso!")
        return 0
    else:
        print("\n❌ Falha ao enviar alerta diário")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 