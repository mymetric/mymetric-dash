import requests
import streamlit as st
import sys
import json
from datetime import datetime, timedelta
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

# Importar módulos do projeto
from modules.load_data import load_internal_events, load_clients

def load_test_groups():
    """Carrega os grupos de teste do arquivo alert_config.json."""
    config_path = os.path.join(os.path.dirname(current_dir), 'usage_metrics', 'alert_config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('test_groups', [])
    except Exception as e:
        print(f"❌ Erro ao carregar grupos de teste: {str(e)}")
        return []

def send_whatsapp_message(message, phone):
    """
    Envia uma mensagem via WhatsApp usando o Z-API.
    
    Args:
        message (str): Mensagem a ser enviada
        phone (str): Número do telefone ou ID do grupo
    """
    try:
        # Configurações do Z-API
        zapi_payload = {
            "phone": phone,
            "message": message
        }

        # Enviar para o Z-API
        response = requests.post(
            st.secrets["zapi"]["url"],
            json=zapi_payload,
            headers={"Client-Token": st.secrets["zapi"]["client_token"]}
        )

        if response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso para {phone}!")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem para {phone}: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para {phone}: {str(e)}")
        return False

def get_hub_usage():
    """
    Retorna métricas de uso de ontem e do mês inteiro.
    """
    try:
        df = load_internal_events()
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('America/Sao_Paulo')
        
        hoje = pd.Timestamp.now(tz='America/Sao_Paulo').date()
        ontem = hoje - timedelta(days=1)
        primeiro_dia_mes = hoje.replace(day=1)
        
        # Dados de ontem
        df_ontem = df[df['created_at'].dt.date == ontem]
        df_logins_ontem = df_ontem[df_ontem['event_name'] == 'login']
        df_filtered_ontem = df_ontem[~df_ontem['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
        
        # Dados do mês (até ontem)
        df_mes = df[(df['created_at'].dt.date >= primeiro_dia_mes) & (df['created_at'].dt.date <= ontem)]
        df_logins_mes = df_mes[df_mes['event_name'] == 'login']
        df_filtered_mes = df_mes[~df_mes['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
        
        clients_df = load_clients()
        total_clientes = len(clients_df) if not clients_df.empty else 0
        
        # Ontem
        clientes_ativos_ontem = df_logins_ontem['tablename'].nunique() if not df_logins_ontem.empty else 0
        usuarios_ativos_ontem = df_ontem['user'].nunique() if not df_ontem.empty else 0
        usuarios_reais_ontem = df_filtered_ontem['user'].nunique() if not df_filtered_ontem.empty else 0
        total_eventos_ontem = len(df_ontem) if not df_ontem.empty else 0
        taxa_ativacao_ontem = (clientes_ativos_ontem / total_clientes * 100) if total_clientes > 0 else 0
        top_empresas_ontem = (df_ontem.groupby('tablename').size().sort_values(ascending=False).head(5))
        top_usuarios_ontem = (df_filtered_ontem.groupby('user').size().sort_values(ascending=False).head(5))
        top_abas_ontem = (df_ontem.groupby('tab').size().sort_values(ascending=False).head(5))
        
        # Mês
        clientes_ativos_mes = df_logins_mes['tablename'].nunique() if not df_logins_mes.empty else 0
        usuarios_ativos_mes = df_mes['user'].nunique() if not df_mes.empty else 0
        usuarios_reais_mes = df_filtered_mes['user'].nunique() if not df_filtered_mes.empty else 0
        total_eventos_mes = len(df_mes) if not df_mes.empty else 0
        taxa_ativacao_mes = (clientes_ativos_mes / total_clientes * 100) if total_clientes > 0 else 0
        top_empresas_mes = (df_mes.groupby('tablename').size().sort_values(ascending=False).head(5))
        top_usuarios_mes = (df_filtered_mes.groupby('user').size().sort_values(ascending=False).head(5))
        top_abas_mes = (df_mes.groupby('tab').size().sort_values(ascending=False).head(5))
        
        return {
            'ontem': {
                'clientes_ativos': clientes_ativos_ontem,
                'usuarios_ativos': usuarios_ativos_ontem,
                'usuarios_reais': usuarios_reais_ontem,
                'total_eventos': total_eventos_ontem,
                'taxa_ativacao': taxa_ativacao_ontem,
                'top_empresas': top_empresas_ontem,
                'top_usuarios': top_usuarios_ontem,
                'top_abas': top_abas_ontem,
                'data': ontem
            },
            'mes': {
                'clientes_ativos': clientes_ativos_mes,
                'usuarios_ativos': usuarios_ativos_mes,
                'usuarios_reais': usuarios_reais_mes,
                'total_eventos': total_eventos_mes,
                'taxa_ativacao': taxa_ativacao_mes,
                'top_empresas': top_empresas_mes,
                'top_usuarios': top_usuarios_mes,
                'top_abas': top_abas_mes,
                'data_inicio': primeiro_dia_mes,
                'data_fim': ontem
            },
            'total_clientes': total_clientes
        }
    except Exception as e:
        print(f"❌ Erro ao analisar uso do hub: {str(e)}")
        return None

def format_usage_message(usage_data):
    """
    Formata os dados de uso em uma mensagem para WhatsApp.
    """
    if not usage_data:
        return "❌ Erro ao gerar relatório de uso do hub"
    
    ontem = usage_data['ontem']['data']
    mes_ini = usage_data['mes']['data_inicio']
    mes_fim = usage_data['mes']['data_fim']
    msg = f"""
📊 *RELATÓRIO DE USO DO HUB*

📅 *Resumo de Ontem* ({ontem.strftime('%d/%m/%Y')})
• Clientes ativos: {usage_data['ontem']['clientes_ativos']}
• Taxa de ativação: {usage_data['ontem']['taxa_ativacao']:.1f}%
• Usuários únicos: {usage_data['ontem']['usuarios_reais']}
• Total de eventos: {usage_data['ontem']['total_eventos']}

🏆 *TOP 5 Empresas (Ontem)*\n"""
    if not usage_data['ontem']['top_empresas'].empty:
        for i, (empresa, eventos) in enumerate(usage_data['ontem']['top_empresas'].items(), 1):
            msg += f"{i}. {empresa}: {eventos} eventos\n"
    else:
        msg += "Nenhuma empresa ativa ontem\n"
    msg += "\n👤 *TOP 5 Usuários (Ontem)*\n"
    if not usage_data['ontem']['top_usuarios'].empty:
        for i, (usuario, eventos) in enumerate(usage_data['ontem']['top_usuarios'].items(), 1):
            msg += f"{i}. {usuario}: {eventos} eventos\n"
    else:
        msg += "Nenhum usuário ativo ontem\n"
    msg += "\n📑 *TOP 5 Abas (Ontem)*\n"
    if not usage_data['ontem']['top_abas'].empty:
        for i, (aba, acessos) in enumerate(usage_data['ontem']['top_abas'].items(), 1):
            msg += f"{i}. {aba}: {acessos} acessos\n"
    else:
        msg += "Nenhuma aba acessada ontem\n"
    msg += f"""

📅 *Resumo do Mês* ({mes_ini.strftime('%d/%m')} a {mes_fim.strftime('%d/%m')})
• Clientes ativos: {usage_data['mes']['clientes_ativos']}
• Taxa de ativação: {usage_data['mes']['taxa_ativacao']:.1f}%
• Usuários únicos: {usage_data['mes']['usuarios_reais']}
• Total de eventos: {usage_data['mes']['total_eventos']}

🏆 *TOP 5 Empresas (Mês)*\n"""
    if not usage_data['mes']['top_empresas'].empty:
        for i, (empresa, eventos) in enumerate(usage_data['mes']['top_empresas'].items(), 1):
            msg += f"{i}. {empresa}: {eventos} eventos\n"
    else:
        msg += "Nenhuma empresa ativa no mês\n"
    msg += "\n👤 *TOP 5 Usuários (Mês)*\n"
    if not usage_data['mes']['top_usuarios'].empty:
        for i, (usuario, eventos) in enumerate(usage_data['mes']['top_usuarios'].items(), 1):
            msg += f"{i}. {usuario}: {eventos} eventos\n"
    else:
        msg += "Nenhum usuário ativo no mês\n"
    msg += "\n📑 *TOP 5 Abas (Mês)*\n"
    if not usage_data['mes']['top_abas'].empty:
        for i, (aba, acessos) in enumerate(usage_data['mes']['top_abas'].items(), 1):
            msg += f"{i}. {aba}: {acessos} acessos\n"
    else:
        msg += "Nenhuma aba acessada no mês\n"
    # Insights
    msg += "\n💡 *INSIGHTS*\n"
    if usage_data['ontem']['taxa_ativacao'] < 20:
        msg += "⚠️ Taxa de ativação baixa ontem\n"
    elif usage_data['ontem']['taxa_ativacao'] > 50:
        msg += "✅ Excelente taxa de ativação ontem!\n"
    if usage_data['ontem']['total_eventos'] < 100:
        msg += "📉 Volume de eventos baixo ontem\n"
    elif usage_data['ontem']['total_eventos'] > 500:
        msg += "📈 Alto volume de eventos ontem!\n"
    if usage_data['ontem']['usuarios_reais'] < 5:
        msg += "👥 Poucos usuários ativos ontem\n"
    if usage_data['mes']['taxa_ativacao'] < 20:
        msg += "⚠️ Taxa de ativação baixa no mês\n"
    elif usage_data['mes']['taxa_ativacao'] > 50:
        msg += "✅ Excelente taxa de ativação no mês!\n"
    if usage_data['mes']['total_eventos'] < 100:
        msg += "📉 Volume de eventos baixo no mês\n"
    elif usage_data['mes']['total_eventos'] > 500:
        msg += "📈 Alto volume de eventos no mês!\n"
    if usage_data['mes']['usuarios_reais'] < 5:
        msg += "👥 Poucos usuários ativos no mês\n"
    return msg

def send_daily_hub_usage_alert(phone, testing_mode=False):
    """
    Envia alerta de uso diário do hub para WhatsApp.
    
    Args:
        phone (str): Número do telefone ou ID do grupo
        testing_mode (bool): Se True, envia mensagem de teste
    """
    try:
        if testing_mode:
            message = """
📊 *RELATÓRIO DE USO DO HUB*

*Esta é uma mensagem de teste para verificar o funcionamento do sistema de alertas de uso diário do hub.*
"""
            return send_whatsapp_message(message, phone)
        
        print("📊 Gerando relatório de uso do hub...")
        
        # Obter dados de uso
        usage_data = get_hub_usage()
        
        if not usage_data:
            error_message = "❌ Erro ao gerar relatório de uso do hub"
            return send_whatsapp_message(error_message, phone)
        
        # Formatar mensagem
        message = format_usage_message(usage_data)
        
        # Enviar mensagem
        return send_whatsapp_message(message, phone)
        
    except Exception as e:
        print(f"❌ Erro ao enviar alerta de uso diário: {str(e)}")
        error_message = f"❌ Erro ao enviar alerta de uso diário: {str(e)}"
        return send_whatsapp_message(error_message, phone)

def send_alerts_to_test_groups(test_mode=False):
    """
    Envia alertas de uso diário para grupos de teste.
    """
    try:
        test_groups = load_test_groups()
        if not test_groups:
            print("❌ Nenhum grupo de teste configurado no alert_config.json!")
            return False
        success_count = 0
        total_count = len(test_groups)
        for group_id in test_groups:
            print(f"📤 Enviando alerta para grupo: {group_id}")
            if send_daily_hub_usage_alert(group_id, test_mode):
                success_count += 1
            else:
                print(f"❌ Falha ao enviar para grupo: {group_id}")
        print(f"✅ Alertas enviados: {success_count}/{total_count}")
        return success_count == total_count
    except Exception as e:
        print(f"❌ Erro ao enviar alertas para grupos de teste: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testando sistema de alertas de uso diário do hub...")
    test_groups = load_test_groups()
    if not test_groups:
        print("❌ Nenhum grupo de teste configurado no alert_config.json!")
    else:
        for test_group in test_groups:
            send_daily_hub_usage_alert(test_group, testing_mode=True) 